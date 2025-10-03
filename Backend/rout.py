import os
import sqlite3
from flask import Flask, render_template, request, flash, session
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




@app.route('/logout')
def logout():
    return render_template("logout.html")

@app.route('/budget')
def budget():   
    return render_template("budget.html")

@app.route('/reports')
def reports():    
    return render_template("reports.html")





@app.route('/upload')
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
