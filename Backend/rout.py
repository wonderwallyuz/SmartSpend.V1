import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from flask import redirect, url_for

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "../Frontend/Public")
DB_PATH = os.path.join(BASE_DIR, "../DataBase/expenses.db")
app = Flask(__name__, template_folder="../Frontend/Public", static_folder="../Frontend/Public")


# --- Flask setup ---
# 👇 Make Public act as both templates and static
app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=TEMPLATE_DIR
)

@app.route('/upload')
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT description, amount, date FROM expenses ORDER BY id DESC LIMIT 5")
    expenses = c.fetchall()
    conn.close()

    return render_template("upload.html", expenses=expenses)

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


@app.route('/')
def bud():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Fetch last 5 budgets
    c.execute("SELECT period, amount, date FROM budgettbl ORDER BY id DESC LIMIT 5")
    budget = c.fetchall()
    conn.close()
    
    # Pass to template
    return render_template("budget.html", budget=budget)


@app.route('/submit-budget', methods=['POST'])
def submit_budget():
    period = request.form.get('period')
    amount = float(request.form.get('amount'))
    date = request.form.get('date')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO budgettbl (period, amount, date) VALUES (?, ?, ?)",
        (period, amount, date)
    )
    conn.commit()
    conn.close()

    # Redirect back to budget page
    return redirect(url_for('bud'))


if __name__ == "__main__":
    app.run(debug=True)
