# setup_login.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Change: Add channel="msedge"
    # This tells Playwright to look for your installed Edge browser
    browser = p.chromium.launch(channel="msedge", headless=False)

    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.linkedin.com/login")

    print("Please log in manually inside the Edge browser...")
    input("Press Enter here in the terminal AFTER you have successfully logged in.")

    # Save the login state (cookies)
    context.storage_state(path="auth.json")
    print("Login saved to auth.json using Edge!")
    browser.close()