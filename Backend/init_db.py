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

c.execute("""
    CREATE TABLE IF NOT EXISTS budgettbl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL
)""")

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

# Save and close
conn.commit()
conn.close()
