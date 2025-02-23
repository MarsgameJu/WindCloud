from flask import Flask, render_template, request, redirect, session, url_for, flash, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
import sqlite3
import bcrypt
import pyotp
from utils.database import get_db
from utils.security import hash_password, verify_password, generate_totp_secret, get_totp_uri, verify_totp
import config
import time
import qrcode
import os
import urllib.parse
from io import BytesIO
import base64
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(config)

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Enable Session & Rate-Limiting
Session(app)
limiter = Limiter(key_func=get_remote_address, default_limits=[config.RATE_LIMIT])
limiter.init_app(app)


def generate_qr_code(uri):
    img = qrcode.make(uri)
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# Database connection and insert function
def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'users.db')
    conn = sqlite3.connect(db_path)
    return conn

def insert_user_to_db(username, email, hashed_pw, totp_secret):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password, totp_secret) VALUES (?, ?, ?, ?)",
                       (username, email, hashed_pw, totp_secret))
        conn.commit()
        conn.close()  # Close connection after commit
    except sqlite3.OperationalError:
        time.sleep(1)  # Wait briefly and try again
        insert_user_to_db(username, email, hashed_pw, totp_secret)

# Database functions for cards
def create_cards_table():
    """Create necessary database tables for cards, files, and sharing if they don't exist"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            type TEXT NOT NULL,
            size INTEGER NOT NULL,
            is_image INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (card_id) REFERENCES cards (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS card_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            shared_with_email TEXT NOT NULL,
            permission TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (card_id) REFERENCES cards (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

# Create tables on startup
create_cards_table()

def init_db():
    """Initialize the database."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Initialize the database if it doesn't exist
if not os.path.exists('database.db'):
    init_db()

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password, totp_secret FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and verify_password(password, user[1]):
            session["temp_user_id"] = user[0]
            session["temp_totp_secret"] = user[2]
            return redirect(url_for("verify_2fa"))  # Redirect to 2FA verification
        else:
            flash("Invalid login credentials.", "warning") #flash message

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm-password"]  # Confirmation password

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))  # Back to registration if passwords do not match

        hashed_pw = hash_password(password)
        totp_secret = generate_totp_secret()

        try:
            insert_user_to_db(username, email, hashed_pw, totp_secret)
            flash("Registration successful! Set up 2FA now.", "success")
            return redirect(url_for("show_2fa", email=email))  # Redirect to 2FA setup
        except sqlite3.IntegrityError:
            flash("Username or email already taken.", "danger")
    
    return render_template("register.html")

@app.route("/2fa/<email>", methods=["GET", "POST"])
def show_2fa(email):
    # Connect to database and retrieve user's TOTP secret
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT totp_secret FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("register"))

    secret = user[0]
    
    # URL-encoded email address
    encoded_email = urllib.parse.quote(email)
    
    # Generate URI for QR code
    totp_uri = f"otpauth://totp/SecureLoginApp:{encoded_email}?secret={secret}&issuer=SecureLoginApp"
    
    # Generate QR code from URI
    img = qrcode.make(totp_uri)
    
    # Save QR code to BytesIO stream
    img_stream = io.BytesIO()
    img.save(img_stream, format='PNG')
    img_stream.seek(0)

    # Provide QR code as base64-encoded image for template
    img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

    if request.method == "POST":
        # User has entered 2FA code, so verify
        code = request.form["code"]
        
        # Verify TOTP code
        if verify_totp(secret, code):
            # Code is correct, log user in and redirect
            flash("2FA successful!", "success")
            return redirect(url_for("login"))
        else:
            flash("Invalid 2FA code. Please try again.", "danger")

    return render_template("2fa.html", totp_uri=totp_uri, img_base64=img_base64)


@app.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    if "temp_user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        code = request.form["code"]
        if verify_totp(session["temp_totp_secret"], code):
            session["user_id"] = session.pop("temp_user_id")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid 2FA code.", "danger")

    return render_template("2fa.html")

@app.route("/dashboard")
def dashboard():
    """Main dashboard view showing user's cards and shared cards"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get user info
    cursor.execute("SELECT email, username FROM users WHERE id = ?", (session["user_id"],))
    user = cursor.fetchone()
    if not user:
        session.clear()
        return redirect(url_for("login"))
    
    # Get user's cards and shared cards
    cursor.execute("""
        SELECT DISTINCT c.id, c.title, c.description, c.created_at, c.updated_at,
               u.username as owner_name,
               CASE WHEN c.user_id = ? THEN 1 ELSE 0 END as is_owner,
               CASE WHEN cs.permission = 'edit' THEN 1 ELSE 0 END as can_edit
        FROM cards c
        LEFT JOIN card_shares cs ON c.id = cs.card_id
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.user_id = ? OR cs.user_id = ?
        GROUP BY c.id
        ORDER BY c.updated_at DESC
    """, (session["user_id"], session["user_id"], session["user_id"]))
    cards = cursor.fetchall()
    
    conn.close()
    
    return render_template("dashboard.html", current_user={"id": session["user_id"], "email": user[0], "username": user[1]}, cards=cards)

@app.route("/api/cards", methods=["POST"])
def create_card():
    """Create a new card"""
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")

    if not title:
        return {"error": "Title is required"}, 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO cards (user_id, title, description) VALUES (?, ?, ?)",
            (session["user_id"], title, description)
        )
        card_id = cursor.lastrowid
        conn.commit()

        # Return the created card
        cursor.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
        card = cursor.fetchone()
        return {
            "id": card[0],
            "title": card[2],
            "description": card[3],
            "created_at": card[4]
        }
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}, 500

@app.route("/api/cards/<int:card_id>", methods=["PUT", "DELETE"])
def manage_card(card_id):
    """Update or delete a card"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM cards WHERE id = ?", (card_id,))
        card = cursor.fetchone()

        if not card:
            return {"error": "Card not found"}, 404
        
        # Check if user has permission
        if card[0] != session["user_id"]:
            cursor.execute(
                "SELECT permission FROM card_shares WHERE card_id = ? AND user_id = ?", 
                (card_id, session["user_id"])
            )
            share = cursor.fetchone()
            if not share or (request.method == "DELETE" and share[0] != "write"):
                return {"error": "Permission denied"}, 403

        if request.method == "DELETE":
            # Delete associated files first
            cursor.execute("SELECT filename FROM files WHERE card_id = ?", (card_id,))
            files = cursor.fetchall()
            for file in files:
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], file[0])
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            cursor.execute("DELETE FROM files WHERE card_id = ?", (card_id,))
            cursor.execute("DELETE FROM card_shares WHERE card_id = ?", (card_id,))
            cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
            conn.commit()
            return {"message": "Card deleted successfully"}

        elif request.method == "PUT":
            data = request.get_json()
            title = data.get("title")
            description = data.get("description")
            
            if not title:
                return {"error": "Title is required"}, 400

            cursor.execute(
                "UPDATE cards SET title = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (title, description, card_id)
            )
            conn.commit()
            return {"message": "Card updated successfully"}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}, 500

@app.route("/api/cards/<int:card_id>/files", methods=["POST"])
def upload_files(card_id):
    """Upload files to a card"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM cards WHERE id = ?", (card_id,))
        card = cursor.fetchone()

        if not card:
            print(f"Card not found: {card_id}")  # Debug log
            return {"error": "Card not found"}, 404
        
        # Check if user has permission
        if card[0] != session["user_id"]:
            cursor.execute(
                "SELECT permission FROM card_shares WHERE card_id = ? AND user_id = ?", 
                (card_id, session["user_id"])
            )
            share = cursor.fetchone()
            if not share or share[0] != "write":
                print(f"Permission denied for user {session['user_id']} on card {card_id}")  # Debug log
                return {"error": "Permission denied"}, 403

        if "files[]" not in request.files:
            print("No files provided in request")  # Debug log
            return {"error": "No files provided"}, 400

        files = request.files.getlist("files[]")
        file_type = request.form.get("type", "file")
        uploaded_files = []
        print(f"Received {len(files)} files for upload")  # Debug log

        for file in files:
            if file and allowed_file(file.filename):
                # Secure the filename
                filename = secure_filename(file.filename)
                # Add timestamp to prevent filename conflicts
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{int(time.time())}{ext}"
                
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                print(f"Saving file to: {file_path}")  # Debug log
                file.save(file_path)

                try:
                    # Get file size
                    file_size = os.path.getsize(file_path)
                    
                    # Create file record
                    cursor.execute(
                        "INSERT INTO files (card_id, name, path, type, size, is_image) VALUES (?, ?, ?, ?, ?, ?)",
                        (card_id, secure_filename(file.filename), file_path, file_type, file_size, file_type == "image")
                    )
                    file_id = cursor.lastrowid
                    print(f"File record created with ID: {file_id}")  # Debug log
                    
                    uploaded_files.append({
                        "id": file_id,
                        "name": secure_filename(file.filename),
                        "url": f"/uploads/{filename}",
                        "is_image": file_type == "image"
                    })
                except sqlite3.Error as e:
                    print(f"Database error: {str(e)}")  # Debug log
                    raise

        conn.commit()
        print(f"Successfully uploaded {len(uploaded_files)} files")  # Debug log
        return {"files": uploaded_files}

    except Exception as e:
        print(f"Error in upload_files: {str(e)}")  # Debug log
        if conn:
            conn.rollback()
        return {"error": str(e)}, 500

@app.route("/api/cards/<int:card_id>/files/<int:file_id>", methods=["DELETE"])
def delete_file(card_id, file_id):
    """Delete a file from a card"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get card info
        cursor.execute("SELECT user_id FROM cards WHERE id = ?", (card_id,))
        card = cursor.fetchone()

        if not card:
            return {"error": "Card not found"}, 404

        # Check if user has permission
        if card[0] != session["user_id"]:
            cursor.execute(
                "SELECT permission FROM card_shares WHERE card_id = ? AND user_id = ?", 
                (card_id, session["user_id"])
            )
            share = cursor.fetchone()
            if not share or share[0] != "write":
                return {"error": "Permission denied"}, 403

        # Get file info
        cursor.execute("SELECT name FROM files WHERE id = ? AND card_id = ?", (file_id, card_id))
        file = cursor.fetchone()

        if not file:
            return {"error": "File not found"}, 404

        # Delete the physical file
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file[0])
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete the database record
        cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()
        return {"message": "File deleted successfully"}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}, 500

@app.route("/api/cards/<int:card_id>/share", methods=["POST"])
def share_card(card_id):
    """Share a card with another user"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM cards WHERE id = ?", (card_id,))
        card = cursor.fetchone()

        if not card:
            return {"error": "Card not found"}, 404
        
        # Check if user owns the card
        if card[0] != session["user_id"]:
            return {"error": "Only the owner can share the card"}, 403

        data = request.get_json()
        email = data.get("email")
        permission = data.get("permission", "read")

        if not email:
            return {"error": "Email is required"}, 400

        # Find user by email
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if not user:
            return {"error": "User not found"}, 404

        # Check if already shared
        cursor.execute(
            "SELECT 1 FROM card_shares WHERE card_id = ? AND user_id = ?", 
            (card_id, user[0])
        )
        if cursor.fetchone():
            return {"error": "Card is already shared with this user"}, 400

        # Create share record
        cursor.execute(
            "INSERT INTO card_shares (card_id, user_id, shared_with_email, permission) VALUES (?, ?, ?, ?)",
            (card_id, user[0], email, permission)
        )
        conn.commit()

        return {"message": "Card shared successfully"}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}, 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            as_attachment=False
        )
    except Exception as e:
        print(f"Error serving file {filename}: {str(e)}")
        return {"error": "File not found"}, 404

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
