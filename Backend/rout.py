import os
import sqlite3
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.abspath(os.path.join(BASE_DIR, "../Frontend/Public"))
UPLOAD_FOLDER = os.path.join(TEMPLATE_DIR, "uploads")
DB_PATH = os.path.join(BASE_DIR, "../DataBase/profile.db")

# --- Create upload directory if not exist ---
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Allowed image extensions ---
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# --- Flask App ---
app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# --- DB Connection Function ---
def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- ROUTES ----------
@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/budget')
def budget():
    return render_template('budget.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')


# ---------- Serve Static Files ----------
@app.route("/<path:filename>")
def serve_static_files(filename):
    return send_from_directory(TEMPLATE_DIR, filename)

# ---------- Serve Uploaded Images ----------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------- API ----------
@app.route("/api/profile", methods=["GET"])
def get_profiles():
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM profile").fetchall()
        conn.close()

        profiles = [
            {key: row[key] for key in row.keys()}
            for row in rows
        ]
        return jsonify(profiles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/profile/update", methods=["POST"])
def insert_profile():
    try:
        data = request.get_json() if request.is_json else request.form

        full_name = data.get("full_name", "")
        username = data.get("username", "")
        email = data.get("email", "")
        role = data.get("role", "")
        bio = data.get("bio", "")
        photo = data.get("photo", "")

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO profile (full_name, username, email, role, bio)
            VALUES (?, ?, ?, ?, ?)
        """, (full_name, username, email, role, bio))
        conn.commit()
        conn.close()
        return jsonify({"message": " New profile added successfully ✅"})

    except sqlite3.IntegrityError as e:
        return jsonify({"error": f"❌ Username or Email already exists: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"❌ Failed to save profile: {e}"}), 500


@app.route("/api/profile/upload_photo", methods=["POST"])
def upload_photo():
    try:
        if "photo" not in request.files:
            return jsonify({"error": "No photo uploaded"}), 400

        file = request.files["photo"]

        if file.filename == "":
            return jsonify({"error": "Empty file name"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Only images are allowed"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        return jsonify({
            "message": " Photo uploaded successfully ✅",
            "photo": f"uploads/{filename}"
        })
    except Exception as e:
        return jsonify({"error": f"❌ Upload failed: {e}"}), 500


# ---------- RUN FLASK ----------
if __name__ == "__main__":
    print(f"📂 Template Folder: {TEMPLATE_DIR}")
    print(f"📂 Database Path: {DB_PATH}")
    app.run(debug=True, use_reloader=False)
