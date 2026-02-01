import schedule
import time
import random
from datetime import datetime, timedelta, timezone
import job_scraper
import connector
import intelligence
import os
import reporter

# Configuration Files
MANUAL_FILE = "manual_targets.txt"
AUTO_FILE = "auto_targets.txt"

def get_combined_targets():
    """Reads both manual and auto lists and merges them."""
    targets = set()

    # 1. Load User's Manual List
    if os.path.exists(MANUAL_FILE):
        with open(MANUAL_FILE, "r") as f:
            manual_list = [line.strip() for line in f.readlines() if line.strip()]
            targets.update(manual_list)
            print(f"   Loaded {len(manual_list)} manual targets.")
    else:
        print(f"   ⚠️ {MANUAL_FILE} not found. Please create it.")

    # 2. Load Intelligence List
    if os.path.exists(AUTO_FILE):
        with open(AUTO_FILE, "r") as f:
            auto_list = [line.strip() for line in f.readlines() if line.strip()]
            targets.update(auto_list)
            print(f"   Loaded {len(auto_list)} auto-discovered targets.")
    else:
        print("   No auto-targets found yet (Run intelligence.py to generate).")

    return list(targets)

def run_daily_analysis():
    """Runs the market research script to populate auto_targets.txt"""
    print("\n--- 🧠 Running Daily Market Intelligence ---")
    intelligence.run_intelligence()

def job_analysis_mode():
    """Mode A: Scrapes fresh job postings"""
    print("\n--- 🔍 Starting Job Analysis Mode ---")
    companies = job_scraper.get_hiring_companies()

    if companies:
        target = random.choice(companies)
        print(f"Targeting recently hiring company: {target}")
        connector.send_requests(target, limit=2)
    else:
        print("No hiring companies found, falling back to Big Tech.")
        big_tech_mode()

def big_tech_mode():
    """Mode B: Targets specific high-value companies from your lists"""
    print("\n--- 🏢 Starting Targeted Mode ---")

    # Get the master list (Manual + Auto)
    target_list = get_combined_targets()

    if not target_list:
        print(f"❌ No targets found! Please add companies to {MANUAL_FILE}")
        return

    # Pick one random company from the combined pool
    target = random.choice(target_list)
    print(f"🎯 Selected Target: {target}")

    # Fire the connector
    connector.send_requests(target, limit=2)

def scheduled_job():
    # ADJUST TIME FOR INDIA (Server is usually UTC)
    # UTC + 5.5 hours = IST
    india_time = datetime.now(tz=timezone.utc) + timedelta(hours=5, minutes=30)
    current_hour = india_time.hour

    print(f"⏰ Current India Time: {india_time.strftime('%H:%M')}")

    # Run only between 8 AM and 7 PM IST
    if 8 <= current_hour <= 19:
        # 50% chance to target new jobs, 50% chance for big tech
        if random.random() > 0.5:
            job_analysis_mode()
        else:
            big_tech_mode()
    else:
        print("💤 Sleeping (Outside working hours)...")

# --- Scheduler Setup ---

# 1. Market Intelligence: Run every Monday morning
schedule.every().monday.at("09:00").do(run_daily_analysis)

# 2. Connection Bot: Run every hour
schedule.every().hour.at(":15").do(scheduled_job)

# 3. Send Daily report
schedule.every().day.at("22:00").do(reporter.send_daily_report)

print("🚀 Oracle Bot Controller Started. Waiting for schedule...")

# Run immediately once for testing
scheduled_job()

while True:
    schedule.run_pending()
    time.sleep(60)