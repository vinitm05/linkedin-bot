from playwright.sync_api import sync_playwright
import time
import random
import database
from pyvirtualdisplay import Display

TARGET_ROLES = [
    "Engineering Manager",
    "Senior Software Engineer",
    "Technical Lead",
    "Product Manager",
    "Director of Engineering"
]


def send_requests(company_name, limit=2):
    print(f"🤖 Bot initializing for target: {company_name}")
    target_role = random.choice(TARGET_ROLES)
    print(f"   🎯 Strategy: Looking for a '{target_role}'")

    with Display(visible=False, size=(1920,1080)):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(storage_state="auth.json")
            page = context.new_page()

            query = f"{target_role} {company_name}"
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={query}&origin=GLOBAL_SEARCH_HEADER"

            try:
                page.goto(search_url, timeout=60000)
                time.sleep(random.uniform(4, 7))
            except Exception as e:
                print(f"❌ Error loading page: {e}")
                browser.close()
                return

            result_cards = page.locator("li.reusable-search__result-container").all()

            sent_count = 0

            for card in result_cards:
                if sent_count >= limit:
                    break

                try:
                    # 1. Extract Profile URL
                    link_tag = card.locator("a.app-aware-link").first
                    profile_url = link_tag.get_attribute("href")
                    if profile_url: profile_url = profile_url.split("?")[0]

                    # 2. Extract Name (Look for the text inside the link)
                    # We use specific selectors to avoid getting "View Profile" text
                    name_tag = link_tag.locator("span[aria-hidden='true']").first
                    person_name = name_tag.inner_text().strip() if name_tag.count() > 0 else "Unknown"

                    # 3. Extract Position/Headline
                    # Usually in the gray text under the name
                    pos_tag = card.locator(".entity-result__primary-subtitle").first
                    person_position = pos_tag.inner_text().strip() if pos_tag.count() > 0 else target_role

                    # Database Check
                    if database.has_contacted(profile_url):
                        print(f"⏭️ Skipping {person_name} (Already contacted)")
                        continue

                    # Connect Logic
                    connect_btn = card.get_by_role("button", name="Connect")
                    if connect_btn.count() > 0:
                        connect_btn.scroll_into_view_if_needed()
                        time.sleep(random.uniform(1, 3))
                        connect_btn.click()

                        time.sleep(1)
                        send_btn = page.get_by_role("button", name="Send without a note")
                        if send_btn.count() > 0:
                            send_btn.click()
                        else:
                            page.get_by_role("button", name="Send", exact=True).click()

                        print(f"✅ Connection sent to: {person_name} ({person_position})")

                        # 4. Log NEW details to Database
                        database.log_contact(profile_url, person_name, company_name, person_position)

                        sent_count += 1
                        time.sleep(random.uniform(3, 8))

                except Exception as e:
                    # print(f"⚠️ Error parsing card: {e}") # Uncomment for debugging
                    continue

            browser.close()
