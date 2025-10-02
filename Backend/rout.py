import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from flask import redirect, url_for

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "../Frontend/Public")
DB_PATH = os.path.join(BASE_DIR, "../DataBase/expenses.db")


# --- Flask setup ---
# 👇 Make Public act as both templates and static
app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=TEMPLATE_DIR
)
"""
@app.route('/')
def landing():
    return render_template("landingpage.html")"""

@app.route('/login')
def login():
    return render_template("login.html")



@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT description, amount, date FROM expenses ORDER BY id DESC LIMIT 5")
    expenses = c.fetchall()
    conn.close()

    # upload.html is directly under Public/
    return render_template("upload.html", expenses=expenses)

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT description, amount FROM expenses ORDER BY id DESC")
    expenses = c.fetchall()
    conn.close()

    return render_template("dashboard.html", expenses=expenses)


@app.route('/submit-expense', methods=['POST']) 
def submit_expense():
    desc = request.form.get('desc')
    amount = float(request.form.get('amount'))
    date = request.form.get('date')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO expenses (description, amount, date) VALUES (?, ?, ?)",
        (desc, amount, date)
    )
    conn.commit()
    conn.close()

    # ✅ redirect back to index (so upload.html is rendered again)
    return redirect(url_for('index'))


    # ✅ return expense data as JSON
    """return jsonify({
        "message": f"Expense '{desc}' saved!",
        "desc": desc,
        "amount": amount,
        "date": date
    })"""

if __name__ == "__main__":
    app.run(debug=True)
