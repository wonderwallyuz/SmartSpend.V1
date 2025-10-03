import sqlite3
import os

os.makedirs('DataBase', exist_ok=True)

conn = sqlite3.connect('DataBase/expenses.db')
c = conn.cursor()

# Recreate table with id as primary key
c.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# ✅ Add email column to existing users table
c.execute("ALTER TABLE users ADD COLUMN email TEXT")




conn.commit()
conn.close()
