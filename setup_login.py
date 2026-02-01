from playwright.sync_api import sync_playwright

# 🛡️ THE MASK (Must match connector.py EXACTLY)
STEALTH_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def login():
    with sync_playwright() as p:
        # Launch visible browser
        browser = p.chromium.launch(headless=False)

        # Create context with the MASK
        context = browser.new_context(
            user_agent=STEALTH_AGENT,
            viewport={"width": 1920, "height": 1080}
        )

        page = context.new_page()

        print("🌍 Going to LinkedIn Login...")
        page.goto("https://www.linkedin.com/login")

        print("⏳ Please log in manually in the browser window...")
        input("✅ Press Enter here AFTER you are fully logged in and see your Feed...")

        # Save the Identity
        context.storage_state(path="auth.json")
        print("💾 auth.json saved with the correct User Agent!")
        browser.close()


if __name__ == "__main__":
    login()