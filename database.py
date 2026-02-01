import sqlite3
import os

DB_NAME = "bot_memory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS contacts
                 (profile_url TEXT PRIMARY KEY, name TEXT, company TEXT, role TEXT, date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def has_contacted(profile_url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT 1 FROM contacts WHERE profile_url=?", (profile_url,))
    result = c.fetchone()
    conn.close()
    return result is not None

def log_contact(profile_url, name, company, role):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO contacts (profile_url, name, company, role) VALUES (?, ?, ?, ?)",
                  (profile_url, name, company, role))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

# Initialize on import
init_db()