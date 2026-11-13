import os
import socket
import sqlite3
import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "jobs.db")
SECRET_KEY = os.environ.get("SECRET_KEY", "jobtrail-secure-jwt-key-production-ready-2026-v1")

app = Flask(__name__)
# Enable CORS for all routes and origins (for mobile apps, PWAs, and local development)
CORS(app, resources={r"/*": {"origins": "*"}})

def get_local_ips():
    ips = []
    try:
        raw_ips = socket.gethostbyname_ex(socket.gethostname())[2]
        for ip in raw_ips:
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    if not ips:
        ips.append("127.0.0.1")
    return ips

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT DEFAULT 'Applied',
            date_applied TEXT,
            interview_date TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Authorization token missing"}), 401
        token = auth.split(" ")[1]
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session expired. Please log in again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token. Please log in again."}), 401
        return f(data["user_id"], *args, **kwargs)
    return wrapper

@app.route("/")
def index():
    html_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(html_path):
        return send_file(html_path)
    return jsonify({"message": "Job Application Tracker API is running"}), 200

@app.route("/manifest.json")
def manifest():
    return send_file(os.path.join(BASE_DIR, "manifest.json"), mimetype="application/manifest+json")

@app.route("/sw.js")
def service_worker():
    return send_file(os.path.join(BASE_DIR, "sw.js"), mimetype="application/javascript")

@app.route("/icon.svg")
def icon_svg():
    return send_file(os.path.join(BASE_DIR, "icon.svg"), mimetype="image/svg+xml")

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are all required."}), 400

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "This email is already registered."}), 409
    finally:
        conn.close()
    return jsonify({"message": "Account created successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    token = jwt.encode(
        {
            "user_id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    })

@app.route("/me", methods=["GET"])
@token_required
def get_current_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(dict(user))

@app.route("/applications", methods=["GET"])
@token_required
def list_applications(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM applications WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/applications", methods=["POST"])
@token_required
def add_application(user_id):
    data = request.get_json() or {}
    company = data.get("company", "").strip()
    role = data.get("role", "").strip()

    if not company or not role:
        return jsonify({"error": "Company and role are required."}), 400

    status = data.get("status", "Applied")
    date_applied = data.get("date_applied") or None
    interview_date = data.get("interview_date") or None
    notes = data.get("notes", "").strip() or None

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO applications (user_id, company, role, status, date_applied, interview_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, company, role, status, date_applied, interview_date, notes)
    )
    new_id = cursor.lastrowid
    conn.commit()
    created = conn.execute("SELECT * FROM applications WHERE id = ?", (new_id,)).fetchone()
    conn.close()

    return jsonify({"message": "Application added successfully", "application": dict(created)}), 201

@app.route("/applications/<int:app_id>", methods=["PUT", "PATCH"])
@token_required
def update_application(user_id, app_id):
    data = request.get_json() or {}
    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM applications WHERE id = ? AND user_id = ?",
        (app_id, user_id)
    ).fetchone()

    if not existing:
        conn.close()
        return jsonify({"error": "Application not found"}), 404

    company = data.get("company", existing["company"]).strip() if "company" in data else existing["company"]
    role = data.get("role", existing["role"]).strip() if "role" in data else existing["role"]
    status = data.get("status", existing["status"])
    date_applied = data.get("date_applied", existing["date_applied"])
    interview_date = data.get("interview_date", existing["interview_date"])
    notes = data.get("notes", existing["notes"])

    if not company or not role:
        conn.close()
        return jsonify({"error": "Company and role cannot be empty."}), 400

    conn.execute(
        """
        UPDATE applications
        SET company = ?, role = ?, status = ?, date_applied = ?, interview_date = ?, notes = ?
        WHERE id = ? AND user_id = ?
        """,
        (company, role, status, date_applied, interview_date, notes, app_id, user_id)
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    conn.close()

    return jsonify({"message": "Application updated successfully", "application": dict(updated)})

@app.route("/applications/<int:app_id>", methods=["DELETE"])
@token_required
def delete_application(user_id, app_id):
    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM applications WHERE id = ? AND user_id = ?",
        (app_id, user_id)
    ).fetchone()

    if not existing:
        conn.close()
        return jsonify({"error": "Application not found"}), 404

    conn.execute("DELETE FROM applications WHERE id = ? AND user_id = ?", (app_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Application deleted successfully"})

if __name__ == "__main__":
    init_db()
    ips = get_local_ips()
    print("=" * 60)
    print(" Jobtrail Server Running")
    print(" -> Local (This PC):    http://localhost:5000")
    for ip in ips:
        print(f" -> Mobile (Same Wi-Fi): http://{ip}:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)