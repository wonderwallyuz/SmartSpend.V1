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
)""")

c.execute("""
    CREATE TABLE IF NOT EXISTS budgettbl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL
)""")

conn.commit()
conn.close()
