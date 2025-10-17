import os
import sqlite3
from flask import Flask, render_template, request, flash, session, json
from flask import redirect, url_for
from ML.MLmodel import categorize_expense
from flask import session
from flask import session, redirect, url_for, flash
import csv
from werkzeug.utils import secure_filename 
from ML.MLmodel import categorize_expense, generate_smartspend_insights


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
    static_folder=os.path.join(BASE_DIR, "../Frontend/Assets")
    
)
app.secret_key = "secret123"

@app.route('/')
def landing():
    return render_template("landingpage.html")

@app.route('/login')
def loginpage():
    return render_template("login.html")

#LOGIN ROUTE
@app.route('/submit-login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM users WHERE email = ? AND password = ?", (email, password))
        user = cur.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]   # use id
            session["username"] = user[1]  # store username
            flash(f"Welcome back, {user[1]}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password!", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route('/signup')
def signuppage():
    return render_template("signup.html")


@app.route("/create-signup", methods=["GET", "POST"])
def signup(): 
    if request.method == "POST":
        username = request.form["username"]  
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("signup"))

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                        (username, password, email))   # 🔄 fixed column order
            conn.commit()
            conn.close()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered!", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")


@app.route('/reports')
def reports():
    username = session.get('username')
    if not username:
        flash("You must be logged in to view reports.", "error")
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ✅ Get all expenses per category
    c.execute("""
        SELECT category, SUM(amount) as total_amount
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY total_amount DESC
    """, (session["user_id"],))
    grouped_expenses = c.fetchall()

    # ✅ Find most active day per category
    c.execute("""
        SELECT 
            category, 
            STRFTIME('%w', date) AS weekday,
            SUM(amount) as total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category, weekday
    """, (session["user_id"],))
    weekday_data = c.fetchall()

    days_map = {
        "0": "Sunday", 
        "1": "Monday", 
        "2": "Tuesday", 
        "3": "Wednesday",
        "4": "Thursday", 
        "5": "Friday", 
        "6": "Saturday"
    }

    from collections import defaultdict
    category_days = defaultdict(lambda: {"day": None, "amount": 0})
    for cat, weekday, total in weekday_data:
    # ✅ Skip invalid weekday values
        if not weekday or weekday not in days_map:
            continue
        if total > category_days[cat]["amount"]:
            category_days[cat] = {"day": days_map[weekday], "amount": total}


    c.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ?", (session["user_id"],))
    total_spent = c.fetchone()[0] or 0
    conn.close()

    breakdown_data = []
    for cat, total_amount in grouped_expenses:
        percent = (total_amount / total_spent * 100) if total_spent else 0
        most_active_day = category_days[cat]["day"] if cat in category_days else "N/A"
        breakdown_data.append((cat, total_amount, percent, most_active_day))

    # ✅ Prepare expense summary and call ML function
    expense_summary = {cat: total_amount for cat, total_amount, _, _ in breakdown_data}
    insights = generate_smartspend_insights(expense_summary)

    return render_template(
        "reports.html",
        username=username,
        breakdown_data=breakdown_data,
        insights=insights
    )







@app.route('/upload')
def index():
    if "user_id" not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT description, amount, date, category
        FROM expenses
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
    """, (session["user_id"],))
    expenses = c.fetchall()
    conn.close()

    return render_template("upload.html", expenses=expenses, username=session["username"])




@app.route('/dashboard')
def dashboard():
    # ✅ Check if user is logged in
    if "user_id" not in session:
        flash("Please log in first!", "error")
        return redirect(url_for("login"))

    username = session["username"]
    user_id = session["user_id"]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ✅ Fetch all expenses belonging to this user
    c.execute("""
        SELECT description, amount, category
        FROM expenses
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))
    expenses = c.fetchall()

    # ✅ Count transactions per category for this user
    c.execute("""
        SELECT category, COUNT(*)
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
    """, (user_id,))
    category_counts = c.fetchall()

    # ✅ Fetch latest budget for this user only
    c.execute("""
        SELECT amount FROM budgettbl
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 1
    """, (user_id,))
    row = c.fetchone()
    if row and row[0] is not None:
        try:
            latest_amount = float(row[0])
        except (ValueError, TypeError):
            latest_amount = 0.0
    else:
        latest_amount = 0.0

    # ✅ Calculate total spent for this user only
    c.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ?", (user_id,))
    sum_row = c.fetchone()
    total_spent = float(sum_row[0]) if sum_row and sum_row[0] is not None else 0.0

    # ✅ Compute remaining budget safely
    remaining = max(latest_amount - total_spent, 0.0)

    conn.close()

    # ✅ Prepare category data dict
    category_data = {cat: count for cat, count in category_counts}

    # ✅ Render user-specific dashboard
    return render_template(
        "dashboard.html",
        username=username,
        expenses=expenses,
        category_data=json.dumps(category_data),
        budget_amount=latest_amount,
        budget_spent=total_spent,
        budget_remaining=remaining
    )



@app.route('/submit-expense', methods=['POST'])
def submit_expense():
    if "user_id" not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for("login"))

    desc = request.form.get('desc')
    amount = float(request.form.get('amount'))
    date = request.form.get('date')

    # Categorize automatically
    category = categorize_expense(desc, amount)

    # Save to database with user_id
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO expenses (user_id, description, amount, date, category)
        VALUES (?, ?, ?, ?, ?)
    """, (session["user_id"], desc, amount, date, category))
    conn.commit()
    
    c.execute("SELECT SUM(amount) FROM expenses")
    sum_row = c.fetchone()
    total_spent = sum_row[0] if sum_row and sum_row[0] is not None else 0.0
    conn.close()
    conn.close()


    flash("Expense added successfully!", "success")
    return redirect(url_for('index', total_spent=total_spent))



#profile section
@app.route('/profile')
def profile():
    print("DEBUG session:", dict(session))   # print everything in session
    username = session.get('username')
    email = session.get('email')
    print("DEBUG username:", username, "email:", email)

    if not username:
        flash("You must be logged in to view dashboard.", "error")
        return redirect(url_for('login'))
    if email:
        flash("Please log in first", "error")
        return redirect(url_for('login'))
    return render_template("profile.html", username=username, email=email)

@app.route('/settings')
def settings():
    username = session.get('username')
    if not username:
        # If user is not logged in, redirect them to login or show error
        flash("You must be logged in to view dashboard.", "error")
        return redirect(url_for('login'))
    return render_template("settings.html", username=username)

@app.route('/help')
def help():
    username = session.get('username')
    if not username:
        # If user is not logged in, redirect them to login or show error
        flash("You must be logged in to view dashboard.", "error")
        return redirect(url_for('login'))
    return render_template("help.html", username=username)

@app.route("/logout")
def logout():
    username = session.get('username')
    if not username:
        # If user is not logged in, redirect them to login or show error
        flash("You must be logged in to view dashboard.", "error")
        return redirect(url_for('login'))
    return render_template("logout.html", username=username)

@app.route('/getting-started')
def getting_started():
    return render_template("gettingstarted.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/FAQ')
def FAQ():
    return render_template("faq.html")


# Budget route
@app.route('/budget')
def budget():
    # ✅ Check if user is logged in
    if "user_id" not in session:
        flash("Please log in first!", "error")
        return redirect(url_for("login"))

    username = session["username"]
    user_id = session["user_id"]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ✅ Get latest budget for this specific user
    c.execute("""
        SELECT period, amount, date 
        FROM budgettbl 
        WHERE user_id = ? 
        ORDER BY id DESC 
        LIMIT 1
    """, (user_id,))
    budget_row = c.fetchone()

    latest_period = budget_row[0] if budget_row and budget_row[0] else "N/A"
    latest_amount = float(budget_row[1]) if budget_row and budget_row[1] else 0.0

    # ✅ Get total spent (only this user's expenses)
    c.execute("""
        SELECT SUM(amount) 
        FROM expenses 
        WHERE user_id = ?
    """, (user_id,))
    sum_row = c.fetchone()
    total_spent = sum_row[0] if sum_row and sum_row[0] else 0.0

    # ✅ Group by category (only this user's expenses)
    c.execute("""
        SELECT 
            GROUP_CONCAT(description, ', '), 
            category, 
            SUM(amount) AS total_amount
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY total_amount DESC
    """, (user_id,))
    grouped_expenses = c.fetchall()
    

    conn.close()

    # ✅ Calculate remaining budget safely
    remaining = max(latest_amount - total_spent, 0.0)
    spent_ratio = 0
    if latest_amount > 0:
        spent_ratio = (total_spent / latest_amount) * 100
        spent_ratio = min(spent_ratio, 100)  # Cap at 100%

    # ✅ Render template with user-specific data
    return render_template(
        "budget.html",
        period=latest_period,
        amount=latest_amount,
        total_spent=total_spent,
        remaining=remaining,
        expenses=grouped_expenses,
        username=username,
        spent_ratio=spent_ratio
    )



@app.route('/submit-budget', methods=['POST'])
def submit_budget():
    if "user_id" not in session:
        flash("Please log in first!", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    period = request.form.get('period')
    amount_str = request.form.get('amount')
    date = request.form.get('date')

    if not (period and amount_str and date):
        return "Missing form data", 400

    try:
        new_amount = float(amount_str)
    except ValueError:
        return "Invalid amount", 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO budgettbl (user_id, period, amount, date) VALUES (?, ?, ?, ?)",
        (user_id, period, new_amount, date)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('budget'))





#csv
@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    if "user_id" not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for("login"))

    if 'file' not in request.files:
        flash("No file part in the request.", "error")
        return redirect(url_for("index"))

    file = request.files['file']
    if file.filename == '':
        flash("No selected file.", "error")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(BASE_DIR, filename)
    file.save(filepath)

    from datetime import datetime
    entries = []

    # Parse CSV or TXT
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            # Expecting: description, amount, date
            if len(row) >= 3:
                desc = row[0].strip()
                try:
                    amount = float(row[1])
                except ValueError:
                    continue

                date_str = row[2].strip()
                if not date_str:
                    continue  # skip empty dates

                # ✅ Normalize and validate date
                parsed_date = None
                for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                if not parsed_date:
                    continue  # skip invalid dates

                date = parsed_date.strftime("%Y-%m-%d")  # normalized format

                # Auto categorize
                category = categorize_expense(desc, amount)
                entries.append((session["user_id"], desc, amount, date, category))

    # ✅ Insert valid rows into DB
    if entries:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.executemany("""
            INSERT INTO expenses (user_id, description, amount, date, category)
            VALUES (?, ?, ?, ?, ?)
        """, entries)
        conn.commit()
        conn.close()
        flash(f"Uploaded {len(entries)} expenses successfully!", "success")
    else:
        flash("No valid rows found in the file (check date format or empty fields).", "error")

    os.remove(filepath)  # Clean up uploaded file
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)
