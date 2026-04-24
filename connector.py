import random
import time

from playwright.sync_api import sync_playwright

import database

# ==========================================
# 🔐 THE MASTER KEYCHAIN
# ==========================================

# The bot will try these one by one until it finds the button
BUTTON_SELECTORS = [
    ".artdeco-button--secondary",  # Standard "Connect" button
    ".artdeco-button--2",  # Standard Variant
    ".artdeco-button",  # Generic
    ".ember-view",  # LinkedIn Framework class
    ".ac1a5614",  # Obfuscated (From your list)
    "button",  # The "Nuclear Option" (Finds any button)
    "_54c2b8d0",
    "b558a3cc",
    "_21eb37b5",
    "d11859ae",
    "eb9355a0",
    "b703709f",
    "_58838fb0",
    "_5a1cdf99", "fca1faf9", "a074e33d", "_57ee4602", "_8b341862", "_60125b54", "e255d55c", "_5f7640a4", "_404a125a",
    "dce7ab81", "be529e0a", "b8e00892", "cc76b7da", "_0f36af5b", "c06f2036"
]

# The bot will try these one by one until it finds the profile cards
CARD_SELECTORS = [
    ".e574b0ac",
    ".ebd90671",
    ".vFMUQgJJxQNkmlCbRjAZxRSLyNNzJYptwAFg",  # Obfuscated (From your list)
    ".tUYHCfcZPxHSbeDWJkCQNrvmjrAHmDzcIE",  # Obfuscated (From your list)
    "li.reusable-search__result-container"  # Specific List Item
]

# ==========================================

TARGET_ROLES = ["Product Manager", "Engineering Manager", "Technical Lead"]
STEALTH_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def send_requests(company_name, limit=2):
    print(f"🤖 Bot initializing for target: {company_name}")
    target_role = random.choice(TARGET_ROLES)

    with sync_playwright() as p:
        # Headless=False so you can watch it pick the lock
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            storage_state="auth.json",
            user_agent=STEALTH_AGENT,
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            query = f"{target_role} {company_name}"
            # Added &origin=GLOBAL_SEARCH_HEADER to match human behavior
            page.goto(f"https://www.linkedin.com/search/results/people/?keywords={query}&origin=GLOBAL_SEARCH_HEADER",
                      timeout=60000)
            time.sleep(5)

            # 🔍 PHASE 1: Find the right Card Selector
            active_card_selector = None
            cards = []

            print("   🕵️‍♂️ Probing for profile cards...")
            for selector in CARD_SELECTORS:
                found = page.locator(selector).all()
                if len(found) > 0:
                    print(f"      ✅ Match found! Using selector: '{selector}' ({len(found)} cards)")
                    active_card_selector = selector
                    cards = found
                    break
                else:
                    # print(f"      ❌ '{selector}' failed.") # Uncomment to debug
                    pass

            if not active_card_selector:
                print("   ❌ CRITICAL: No profile cards found. LinkedIn has changed the code completely.")
                return

            # 🔍 PHASE 2: Process Cards
            sent_count = 0
            for i, card in enumerate(cards):
                if sent_count >= limit: break

                # Try to get the name (Not critical, just for logging)
                try:
                    name_tag = card.locator("span[aria-hidden='true']").first
                    name = name_tag.inner_text().strip() if name_tag.count() > 0 else f"Candidate #{i + 1}"
                except:
                    name = f"Candidate #{i + 1}"

                # 🔍 PHASE 3: Find the right Button Selector inside this card
                clicked = False
                for btn_selector in BUTTON_SELECTORS:
                    # We combine the class with the text "Connect" to be safe
                    btn = card.locator(btn_selector).filter(has_text="Connect")

                    if btn.count() > 0:
                        # Check if it's disabled/pending (has 'muted' class)
                        if "artdeco-button--muted" in btn.get_attribute("class"):
                            print(f"      ⏭️ Skipping {name} (Already Pending)")
                            clicked = True  # Treat as handled
                            break

                        print(f"   👋 Connecting with {name} (Method: {btn_selector})...")
                        try:
                            btn.first.click(force=True)
                        except Exception as e:
                            print(f"⚠️ Force click failed, trying JavaScript click...")
                            btn.first.evaluate("element => element.click()")
                        time.sleep(1)

                        # Handle Popup
                        send = page.locator("button[aria-label='Send now']")
                        if send.count() == 0:
                            send = page.locator("button:has-text('Send without a note')")

                        if send.count() > 0:
                            send.click()
                            print(f"      ✅ SUCCESS.")
                            database.log_contact("unknown", name, company_name, target_role)
                            sent_count += 1
                            time.sleep(random.uniform(3, 6))
                        else:
                            # Close popup if something went wrong
                            page.keyboard.press("Escape")

                        clicked = True
                        break  # Stop checking other button selectors for this person

                if not clicked:
                    # Optional: Check for Follow button just to know
                    # print(f"      ⚠️ No Connect button for {name} (Likely Creator/VIP).")
                    pass

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            browser.close()
