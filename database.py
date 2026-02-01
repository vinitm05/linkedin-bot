import sqlite3
from datetime import datetime

DB_NAME = "bot_memory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Updated Schema: Added 'name' and 'position' columns
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (profile_url text PRIMARY KEY, 
                  name text, 
                  company text, 
                  position text, 
                  date_sent text)''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def has_contacted(profile_url):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM history WHERE profile_url = ?", (profile_url,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Updated to accept 4 arguments instead of 2
def log_contact(profile_url, name, company, position):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO history VALUES (?, ?, ?, ?, ?)",
                  (profile_url, name, company, position, datetime.now().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

init_db()