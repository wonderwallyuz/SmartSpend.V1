import sqlite3
import os

# Ensure database directory exists
os.makedirs('DataBase', exist_ok=True)

# Connect to the database
conn = sqlite3.connect('DataBase/expenses.db')
c = conn.cursor()

# Create users table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)
""")
# Create budget table
c.execute("""
    CREATE TABLE IF NOT EXISTS budgettbl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    period TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT
)
""")

# Create expenses table (linked to user_id)
c.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,          
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read INTEGER DEFAULT 0
)
""")

c = conn.cursor()
c.execute("DELETE FROM expenses WHERE date IS NULL OR TRIM(date) = ''")

print("✅ Cleaned invalid rows")


# Save and close
conn.commit()
conn.close()
