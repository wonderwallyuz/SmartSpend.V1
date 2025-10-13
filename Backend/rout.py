import os
import sqlite3
from flask import Flask, render_template, request, flash, session, json
from flask import redirect, url_for
from ML.MLmodel import categorize_expense
from flask import session
from flask import session, redirect, url_for, flash

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

# ✅ LOGIN ROUTE
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
        username = request.form["username"]   # 🔄 changed fullname → username
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
        # If user is not logged in, redirect them to login or show error
        flash("You must be logged in to view dashboard.", "error")
        return redirect(url_for('login'))
    return render_template("reports.html", username=username,)





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

    # ✅ Connect to DB and fetch data for this user only
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Fetch all expenses belonging to the logged-in user
    c.execute("""
        SELECT description, amount, category
        FROM expenses
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))
    expenses = c.fetchall()

    # Count transactions per category for this user only
    c.execute("""
        SELECT category, COUNT(*)
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
    """, (user_id,))
    category_counts = c.fetchall()
    
    c.execute("SELECT amount FROM budgettbl ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    if row and row[0] is not None:
        try:
            latest_amount = float(row[0])
        except (ValueError, TypeError):
            latest_amount = 0.0
    else:
        latest_amount = 0.0
        
    c.execute("SELECT SUM(amount) FROM expenses")
    sum_row = c.fetchone()
    if sum_row and sum_row[0] is not None:
        total_spent = sum_row[0]
    else:
        total_spent = 0.0
        
    remaining = latest_amount - total_spent
    if remaining < 0:
        remaining = 0.0
        
    c.execute("SELECT description, amount, category FROM expenses ORDER BY id DESC")
    expenses = c.fetchall()

    
    conn.close()
    # turn into dict {category: count}
    # Convert to dict {category: count}
    category_data = {cat: count for cat, count in category_counts}

    # ✅ Pass username and user data to template
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

@app.route('/budget')
def bud():
    username = session.get('username')
    if not username:
        # If user is not logged in, redirect them to login or show error
        flash("You must be logged in to view dashboard.", "error")
        return redirect(url_for('login'))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    total_spent = 0.0
    descriptions = []  # List to hold description values
    categories = [] 
    # Retrieve the latest budget entry
    c.execute("SELECT period, amount, date FROM budgettbl ORDER BY id DESC")
    budget_row = c.fetchone()
    
    # Initialize latest_amount to 0.0 if no budget entry exists
    latest_amount = 0.0
    if budget_row:
        try:
            latest_amount = float(budget_row[1])
        except (ValueError, TypeError):
            latest_amount = 0.0
            
    # Retrieve the total amount spent from expenses
    c.execute("SELECT SUM(amount) FROM expenses")
    sum_row = c.fetchone()
    total_spent = sum_row[0] if sum_row and sum_row[0] is not None else 0.0
    
    c.execute("SELECT description, category, amount FROM expenses ORDER BY id DESC")
    expense_rows = c.fetchall()
    for row in expense_rows:
        descriptions.append(row[0])  # Description
        categories.append(row[1])

    conn.close()

    # Calculate remaining amount
    remaining = latest_amount - total_spent
    if remaining < 0:
        remaining = 0.0

    return render_template(
        "budget.html",
        amount=latest_amount,
        total_spent=total_spent,
        remaining=remaining,
        expenses=expense_rows,
        descriptions=descriptions,
        categories=categories,
        username=username
    )

@app.route('/submit-budget', methods=['POST'])
def submit_budget():
    print("DEBUG form data:", request.form) 
    period = request.form.get('period')
    amount_str = request.form.get('amount')
    date = request.form.get('date')

    if not (period and amount_str and date):
        return "Missing form data", 400
    try:
        amount = float(amount_str)
    except ValueError:
        return "Invalid amount", 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO budgettbl (period, amount, date) VALUES (?, ?, ?)",
        (period, amount, date)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('bud'))


if __name__ == "__main__":
    app.run(debug=True)
