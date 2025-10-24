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
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename


# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "../Frontend/Public")
STATIC_DIR = os.path.join(BASE_DIR, "../Frontend/Assets")
DB_PATH = os.path.join(BASE_DIR, "../DataBase/expenses.db")
UPLOAD_FOLDER = os.path.join(STATIC_DIR, "uploads")

# --- Flask setup ---
app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    static_url_path="/static"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "secret123"


# ✅ Ensure uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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
    
    
    role = session.get("role")  # ✅ Use session first — faster

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # ✅ If role not in session (e.g. user logged in before update), fetch from DB
    if not role:
        c.execute("SELECT role FROM profile WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        role = row[0] if row and row[0] else "User"
        session["role"] = role  # 🔁 Cache it in session for next time

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
        role=role,
        breakdown_data=breakdown_data,
        insights=insights
    )







@app.route('/upload')
def index():
    if "user_id" not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for("login"))
    role = session.get("role")  # ✅ Use session first — faster
    
    # ✅ If role not in session (e.g. user logged in before update), fetch from DB
    if not role:
        c.execute("SELECT role FROM profile WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        role = row[0] if row and row[0] else "User"
        session["role"] = role  # 🔁 Cache it in session for next time

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

    return render_template("upload.html", expenses=expenses, username=session["username"], role=role)









@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        flash("Please log in first!", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    username = session.get("username", "User")
    role = session.get("role")  # ✅ Use session first — faster

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ✅ If role not in session (e.g. user logged in before update), fetch from DB
    if not role:
        c.execute("SELECT role FROM profile WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        role = row[0] if row and row[0] else "User"
        session["role"] = role  # 🔁 Cache it in session for next time

    # ✅ Fetch all user expenses
    c.execute("""
        SELECT description, amount, category
        FROM expenses
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))
    expenses = c.fetchall()

    # ✅ Count per category
    c.execute("""
        SELECT category, COUNT(*)
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
    """, (user_id,))
    category_counts = c.fetchall()

    # ✅ Latest budget
    c.execute("""
        SELECT amount FROM budgettbl
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 1
    """, (user_id,))
    row = c.fetchone()
    latest_amount = float(row[0]) if row and row[0] is not None else 0.0

    # ✅ Total spent
    c.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ?", (user_id,))
    sum_row = c.fetchone()
    total_spent = float(sum_row[0]) if sum_row and sum_row[0] is not None else 0.0

    remaining = max(latest_amount - total_spent, 0.0)
    conn.close()

    # ✅ Prepare category data for charts
    category_data = {cat: count for cat, count in category_counts}

    # ✅ Render dashboard with user-specific data
    return render_template(
        "dashboard.html",
        username=username,
        role=role,  # 👈 Passed to template
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


# =========================
# 👤 VIEW PROFILE PAGE (HTML)
# =========================
@app.route('/profile')
def profile():
    print("DEBUG session:", dict(session))  # For debugging

    # ✅ Check login
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to view your profile.", "error")
        return redirect(url_for("login"))

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # ✅ Get user info from `users`
        c.execute("""
            SELECT username, email
            FROM users
            WHERE id = ?
        """, (user_id,))
        user_row = c.fetchone()

        if not user_row:
            flash("User not found!", "error")
            return redirect(url_for("login"))

        username, email = user_row["username"], user_row["email"]

        # ✅ Get profile info from `profile`
        c.execute("""
            SELECT role, bio, photo
            FROM profile
            WHERE user_id = ?
        """, (user_id,))
        profile_row = c.fetchone()

        if profile_row:
            role, bio, photo = profile_row["role"], profile_row["bio"], profile_row["photo"]
        else:
            role, bio, photo = "User", "", None

        print(f"Loaded profile for user_id={user_id}: username={username}, role={role}")

        return render_template(
            "profile.html",
            username=username,
            email=email,
            role=role,
            bio=bio,
            photo=photo
        )

    except Exception as e:
        flash(f"Error loading profile: {e}", "error")
        return redirect(url_for("dashboard"))
    finally:
        if conn:
            conn.close()

@app.route('/help')
def help():
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    username = session.get('username')
    user_id = session["user_id"]
    if not username:
        # If user is not logged in, redirect them to login or show error
        flash("You must be logged in to view dashboard.", "error")
        return redirect(url_for('login'))
    
    role = session.get("role")  # ✅ Use session first — faster
    # ✅ If role not in session (e.g. user logged in before update), fetch from DB
    if not role:
        c.execute("SELECT role FROM profile WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        role = row[0] if row and row[0] else "User"
        session["role"] = role  # 🔁 Cache it in session for next time
    return render_template("help.html", username=username,role=role)







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
    role = session.get("role")  # ✅ Use session first — faster

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if not role:
        c.execute("SELECT role FROM profile WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        role = row[0] if row and row[0] else "User"
        session["role"] = role  # 🔁 Cache it in session for next time
    
    

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
        spent_ratio=spent_ratio,
        role=role
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



ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# --- Create upload directory if not exist ---
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- DB Connection Function ---
def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- File validation ---
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# =========================
# 👤 GET CURRENT USER PROFILE (API)
# =========================
@app.route("/api/profile", methods=["GET"])
def get_profile():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized. Please log in first."}), 401

    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # ✅ Join users + profile
        row = cursor.execute("""
            SELECT 
                u.username AS username, 
                u.email AS email,
                COALESCE(p.role, 'User') AS role,
                COALESCE(p.bio, '') AS bio,
                p.photo AS photo
            FROM users u
            LEFT JOIN profile p ON u.id = p.user_id
            WHERE u.id = ?
        """, (user_id,)).fetchone()

        conn.close()

        if not row:
            return jsonify({
                "success": True,
                "profile": {
                    "username": session.get("username"),
                    "email": "",
                    "role": "User",
                    "bio": "",
                    "photo": None
                }
            })

        return jsonify({"success": True, "profile": dict(row)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# =========================
# ✏️ UPDATE USER PROFILE (API)
# =========================
@app.route("/api/profile/update", methods=["POST"])
def update_profile():
    conn = None
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized user"}), 401

        # ✅ Collect form data
        username = request.form.get("username", "").strip()
        role = request.form.get("role", "User").strip()
        bio = request.form.get("bio", "").strip()
        photo_file = request.files.get("photo")

        # ✅ Handle photo upload
        photo_url = None
        if photo_file and allowed_file(photo_file.filename):
            filename = f"user{user_id}_{secure_filename(photo_file.filename)}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            photo_file.save(filepath)
            photo_url = url_for("static", filename=f"uploads/{filename}")

        # ✅ DB connection
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")

        # ✅ Check if profile exists
        existing = cursor.execute("SELECT * FROM profile WHERE user_id=?", (user_id,)).fetchone()

        if existing:
            cursor.execute("""
                UPDATE profile
                SET role = ?, 
                    bio = ?, 
                    photo = COALESCE(?, photo)
                WHERE user_id = ?
            """, (role, bio, photo_url, user_id))
        else:
            cursor.execute("""
                INSERT INTO profile (user_id, role, bio, photo)
                VALUES (?, ?, ?, ?)
            """, (user_id, role, bio, photo_url))

        # ✅ Update username only in users table
        if username:
            cursor.execute("UPDATE users SET username=? WHERE id=?", (username, user_id))

        conn.commit()

        # ✅ Refresh session
        session["username"] = username or session.get("username")
        session["role"] = role

        updated_profile = cursor.execute(
            "SELECT * FROM profile WHERE user_id=?", (user_id,)
        ).fetchone()

        return jsonify({
            "success": True,
            "message": "Profile updated successfully ✅",
            "profile": dict(updated_profile),
            "photo_url": photo_url or (updated_profile["photo"] if updated_profile else None)
        })

    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            return jsonify({"success": False, "error": "Database is locked. Try again."}), 500
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Failed to update profile: {e}"}), 500
    finally:
        if conn:
            conn.close()




# =========================
# 🖼️ SEPARATE PHOTO UPLOAD
# =========================
@app.route("/api/profile/upload_photo", methods=["POST"])
def upload_photo():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized user"}), 401

    try:
        file = request.files.get("photo")
        if not file or file.filename == "":
            return jsonify({"error": "No photo uploaded"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Only images are allowed"}), 400

        filename = f"user{user_id}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        photo_url = url_for("static", filename=f"uploads/{filename}")

        # ✅ Update DB using context manager
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE profile SET photo=? WHERE user_id=?", 
                (photo_url, user_id)
            )
            conn.commit()

        return jsonify({
            "message": "Photo uploaded successfully ✅",
            "photo_url": photo_url
        })

    except Exception as e:
        return jsonify({"error": f"Upload failed: {e}"}), 500
    


@app.route('/settings')
def settings():
    # ✅ Require login before accessing settings
    if "user_id" not in session:
        flash("Please log in to access settings.", "error")
        return redirect(url_for('login'))

    # You can also fetch user info to pre-fill email, etc.
    user_email = None
    user_id = session["user_id"]

   
    return render_template('settings.html')


@app.route('/update_password', methods=['POST'])
def update_password():
    # ✅ Ensure user is logged in
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    data = request.get_json()
    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")
    confirm_password = data.get("confirmPassword")

    # ✅ Validate fields
    if not current_password or not new_password or not confirm_password:
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    if new_password != confirm_password:
        return jsonify({"status": "error", "message": "New passwords do not match"}), 400

    user_id = session["user_id"]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ✅ Get current password from DB
    c.execute("SELECT password FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()

    if not result:
        conn.close()
        return jsonify({"status": "error", "message": "User not found"}), 404

    stored_password = result[0]

    # ✅ Check if current password matches
    if stored_password != current_password:
        conn.close()
        return jsonify({"status": "error", "message": "Current password is incorrect"}), 400

    # ✅ Update password in DB
    c.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Password updated successfully!"})

# --- Run App ---
if __name__ == "__main__":
    print(f"📂 Template Folder: {TEMPLATE_DIR}")
    print(f"📂 Static Folder: {STATIC_DIR}")
    print(f"📂 Upload Folder: {UPLOAD_FOLDER}")
    print(f"📂 Database Path: {DB_PATH}")
    app.run(debug=True, use_reloader=False)
