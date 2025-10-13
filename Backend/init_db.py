import sqlite3
import os

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../DataBase/profile.db")

# --- Connect to database ---
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# --- Create profile table if it doesn't exist ---
c.execute("""
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    bio TEXT
)
""")

c.execute("SELECT COUNT(*) FROM profile")
count = c.fetchone()[0]


# --- Commit and close ---
conn.commit()
conn.close()

print("✅ profile table ready with 1 default row")
