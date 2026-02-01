import requests
from bs4 import BeautifulSoup
import random


def get_hiring_companies():
    # Target "Python Developer" in "India"
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Python%20Developer&location=India&f_TPR=r86400"

    # Rotate User-Agents to avoid getting blocked
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
    ]

    headers = {
        "User-Agent": random.choice(user_agents)
    }

    try:
        # Reduced timeout to 5s so the bot doesn't hang if LI is slow
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            print(f"⚠️ Scraper Blocked: Status {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        companies = set()

        # Scrape company names from job cards
        # Note: 'base-card' is the standard class for LI Guest view
        for card in soup.find_all("div", class_="base-card"):
            company_tag = card.find("h4", class_="base-search-card__subtitle")
            if company_tag:
                raw_name = company_tag.get_text(strip=True)
                companies.add(raw_name)

        return list(companies)
    except Exception as e:
        print(f"⚠️ Scrape error: {e}")
        return []