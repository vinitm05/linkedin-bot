import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# 🔒 LOAD SECRETS
load_dotenv() # This looks for the .env file

SENDER_EMAIL = os.getenv("EMAIL_USER")
SENDER_PASSWORD = os.getenv("EMAIL_PASS")
RECEIVER_EMAIL = SENDER_EMAIL # Sending to yourself

DB_NAME = "bot_memory.db"


def get_daily_stats():
    """Queries DB for activity in the last 24 hours."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # SQLite stores time in UTC by default, so we check for records > 24 hours ago
    query = """
            SELECT name, company, role, date_added
            FROM contacts
            WHERE date_added >= datetime('now', '-1 day') \
            """
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    return rows


def send_daily_report():
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("❌ Error: Email credentials not found in .env file.")
        return
    print("📧 Generating Daily Report...")
    data = get_daily_stats()

    if not data:
        print("   No activity today. Skipping email.")
        return

    # Build the HTML Body
    count = len(data)
    html_body = f"""
    <h2>🚀 LinkedIn Bot Daily Report</h2>
    <p><b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}</p>
    <p><b>Total Connections Sent:</b> {count}</p>
    <hr>
    <h3>📝 Activity Log:</h3>
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
        <tr style="background-color: #f2f2f2;">
            <th>Name</th>
            <th>Role</th>
            <th>Company</th>
        </tr>
    """

    for name, company, role, date in data:
        html_body += f"""
        <tr>
            <td>{name}</td>
            <td>{role}</td>
            <td>{company}</td>
        </tr>
        """

    html_body += "</table><br><p><i>Bot is running smooth on Oracle Cloud.</i></p>"

    # Send Email
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = f"📊 Bot Report: {count} Sent Today"
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("   ✅ Email Report Sent Successfully!")
    except Exception as e:
        print(f"❌ Email Failed: {e}")


if __name__ == "__main__":
    # Test run
    send_daily_report()