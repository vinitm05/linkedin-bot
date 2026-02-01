import requests
import json

TARGET_FILE = "auto_targets.txt"

def get_yc_startups():
    print("💰 Scanning YC for recently funded startups...")
    # YC Algolia API (Public endpoint)
    url = "https://443003444r-dsn.algolia.net/1/indexes/examples_PROD_companies/query"

    # Logic: Get top 30 companies from the two most recent batches
    # We look at Winter 2024, Summer 2024, Winter 2025 to keep it fresh
    payload = {
        "params": "query=&hitsPerPage=30&filters=batch:W24 OR batch:S24 OR batch:W25"
    }

    headers = {
        "x-algolia-application-id": "443003444R",
        "x-algolia-api-key": "943e93652f1e9447e17441547470f14c"  # Public search key
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        hits = response.json().get("hits", [])
        companies = [h['name'] for h in hits]
        print(f"   Found {len(companies)} recent YC startups.")
        return companies
    except Exception as e:
        print(f"   YC Error: {e}")
        return []

def get_github_trending_owners():
    print("🔥 Scanning GitHub for trending Python/AI companies...")
    # We look for trending repositories in Python to find companies building cool tech
    url = "https://api.github.com/search/repositories?q=language:python+created:>2024-01-01&sort=stars&order=desc"

    try:
        response = requests.get(url, headers={"User-Agent": "Bot"})
        data = response.json()

        orgs = set()
        for item in data.get("items", [])[:20]:  # Top 20 repos
            # If the owner is an Organization (Company), not a User
            if item['owner']['type'] == 'Organization':
                org_name = item['owner']['login']
                # Clean up name (remove hyphens, etc)
                clean_name = org_name.replace("-", " ").title()
                orgs.add(clean_name)

        print(f"   Found {len(orgs)} trending engineering orgs.")
        return list(orgs)
    except Exception as e:
        print(f"   GitHub Error: {e}")
        return []

def run_intelligence():
    print("🧠 Starting Intelligence Scan...")

    # 1. Fetch Fresh Data
    yc_leads = get_yc_startups()
    git_leads = get_github_trending_owners()

    fresh_leads = set(yc_leads + git_leads)

    # 2. Read Existing Auto-List (Preserve history)
    existing_auto = set()
    try:
        with open(TARGET_FILE, "r") as f:
            existing_auto = {line.strip() for line in f.readlines() if line.strip()}
    except FileNotFoundError:
        print("   No existing auto-list found. Creating new one.")

    # 3. Update Auto-List (Append Only)
    new_count = 0
    with open(TARGET_FILE, "w") as f:  # Re-write file to keep it sorted/clean
        # Combine old + new
        combined = sorted(list(existing_auto.union(fresh_leads)))

        for company in combined:
            f.write(f"{company}\n")

        new_count = len(combined) - len(existing_auto)

    print(f"✅ Intelligence Update Complete.")
    print(f"   - Old Targets: {len(existing_auto)}")
    print(f"   - New Targets Added: {new_count}")
    print(f"   - Total Auto Targets: {len(combined)}")

if __name__ == "__main__":
    run_intelligence()