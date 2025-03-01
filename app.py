import base64
import bcrypt
import config
import io
import os
import pyotp
import qrcode
import re
import sqlite3
import time
import urllib.parse
from io import BytesIO
from flask import Flask, render_template, request, redirect, session, url_for, flash, send_file, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
from flask_session import Session
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.utils import secure_filename
from utils.database import get_db
from utils.security import hash_password, verify_password, generate_totp_secret, get_totp_uri, verify_totp
from utils.error_handler import ErrorHandler

app = Flask(__name__, static_url_path='', static_folder='static')
app.config.from_object(config)

# Create session directory if it doesn't exist
if not os.path.exists(app.config['SESSION_FILE_DIR']):
    os.makedirs(app.config['SESSION_FILE_DIR'])

# Initialize extensions
Session(app)
mail = Mail(app)
error_handler = ErrorHandler(app, debug_mode=app.config.get('DEBUG', False))

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
limiter = Limiter(key_func=get_remote_address, default_limits=[config.RATE_LIMIT])
limiter.init_app(app)

# Initialize serializer for password reset tokens
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

def generate_qr_code(uri):
    img = qrcode.make(uri)
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# Database connection and insert function
def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'users.db')
    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        init_db()
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

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

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
    
    # Get user's cards & shared cards
    cursor.execute("""
        SELECT DISTINCT c.id, c.title, c.description, c.created_at, c.updated_at,
               u.username as owner_name,
               CASE WHEN c.user_id = ? THEN 1 ELSE 0 END as is_owner,
               CASE WHEN c.user_id = ? THEN 1 ELSE (CASE WHEN cs.permission = 'write' THEN 1 ELSE 0 END) END as can_edit
        FROM cards c
        LEFT JOIN card_shares cs ON c.id = cs.card_id
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.user_id = ? OR cs.user_id = ?
        GROUP BY c.id
        ORDER BY c.updated_at DESC
    """, (session["user_id"], session["user_id"], session["user_id"], session["user_id"]))
    cards = cursor.fetchall()
    
    # Für jede Karte Dateien abrufen und trennen in Bilder und andere Dateien
    cards_data = []
    for card in cards:
        card_id = card[0]
        cursor.execute("SELECT id, name, path, is_image FROM files WHERE card_id = ?", (card_id,))
        files = cursor.fetchall()
        images = []
        non_images = []
        for f in files:
            file_obj = {
                "id": f[0],
                "name": f[1],
                "url": "/uploads/" + os.path.basename(f[2]),
                "is_image": bool(f[3])
            }
            if file_obj["is_image"]:
                images.append(file_obj)
            else:
                non_images.append(file_obj)
        cards_data.append({
            "id": card[0],
            "title": card[1],
            "description": card[2],
            "created_at": card[3],
            "updated_at": card[4],
            "owner_name": card[5],
            "is_owner": card[6],
            "can_edit": card[7],
            "images": images,
            "files": non_images
        })
    conn.close()
    
    return render_template("dashboard.html", current_user={"id": session["user_id"], "email": user[0], "username": user[1]}, cards=cards_data)

@app.route("/api/cards", methods=["POST"])
def create_card():
    """Create a new card"""
    if "user_id" not in session:
        return {"error": "Not authenticated"}, 401

    data = request.get_json()
    title = data.get("title")
    description = data.get("description")

    if not title:
        return {"error": "Title is required"}, 400

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO cards (user_id, title, description) VALUES (?, ?, ?)",
            (session["user_id"], title, description)
        )
        card_id = cursor.lastrowid
        conn.commit()

        cursor.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
        card = cursor.fetchone()
        return {
            "id": card[0],
            "title": card[2],
            "description": card[3],
            "created_at": card[4]
        }
    except Exception as e:
        if conn:
            conn.rollback()
        app.logger.error(f"Error creating card: {str(e)}")
        return {"error": "An error occurred while creating the card"}, 500

@app.route("/api/cards/<int:card_id>", methods=["PUT", "DELETE"])
def manage_card(card_id):
    """Update or delete a card"""
    if "user_id" not in session:
        return {"error": "Not authenticated"}, 401
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if card exists
        cursor.execute("SELECT user_id FROM cards WHERE id = ?", (card_id,))
        card = cursor.fetchone()

        if not card:
            return {"error": "Card not found"}, 404
        
        # Updated permission check for both PUT and DELETE:
        if card[0] != session["user_id"]:
            cursor.execute(
                "SELECT permission FROM card_shares WHERE card_id = ? AND user_id = ?", 
                (card_id, session["user_id"])
            )
            share = cursor.fetchone()
            if not share or share[0] != "write":
                flash("No Permisson", "danger")    
                return {"error": "Permission denied: You have read-only access."}, 403


        if request.method == "DELETE":
            try:
                # Delete associated files first
                cursor.execute("SELECT name, path FROM files WHERE card_id = ?", (card_id,))
                files = cursor.fetchall()
                
                # Delete physical files
                for file in files:
                    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file[1])  # Using path instead of name
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except OSError as e:
                            print(f"Error deleting file {file_path}: {e}")
                            # Continue even if file deletion fails
                
                # Delete database records
                cursor.execute("DELETE FROM files WHERE card_id = ?", (card_id,))
                cursor.execute("DELETE FROM card_shares WHERE card_id = ?", (card_id,))
                cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
                conn.commit()
                
                return {"message": "Card deleted successfully"}
                
            except Exception as e:
                conn.rollback()
                print(f"Error during card deletion: {str(e)}")
                app.logger.error(f"Database error: {str(e)}")
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
        app.logger.error(f"Error managing card {card_id}: {str(e)}")
        return {"error": "An error occurred while managing the card"}, 500

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
                    app.logger.error(f"Database error while uploading files: {str(e)}")
                    return {"error": "An error occurred while saving file information"}, 500

        conn.commit()
        print(f"Successfully uploaded {len(uploaded_files)} files")  # Debug log
        return {"files": uploaded_files}

    except Exception as e:
        print(f"Error in upload_files: {str(e)}")  # Debug log
        if conn:
            conn.rollback()
        app.logger.error(f"Error uploading files: {str(e)}")
        return {"error": "An error occurred while uploading files"}, 500

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

        # Retrieve the full file path from the DB
        cursor.execute("SELECT path FROM files WHERE id = ? AND card_id = ?", (file_id, card_id))
        row = cursor.fetchone()
        if not row:
            return {"error": "File not found"}, 404

        file_path = row[0]
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete the database record
        cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()
        return {"message": "File deleted successfully"}

    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error deleting file {file_id} from card {card_id}: {str(e)}")
        return {"error": "An error occurred while deleting the file"}, 500

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
        app.logger.error(f"Error sharing card {card_id}: {str(e)}")
        return {"error": "An error occurred while sharing the card"}, 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files using send_from_directory"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)
    except Exception as e:
        app.logger.error(f"Error serving file {filename}: {str(e)}")
        return {"error": "File not found"}, 404

@app.route("/reset-password", methods=["GET", "POST"])
def reset_request():
    # ...existing code...
    if request.method == "POST":
        email = request.form["email"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if user:
            token = serializer.dumps(email, salt="password-reset-salt")
            reset_link = url_for("reset_token", token=token, _external=True)
            from flask_mail import Message  # ensure import at top if needed
            msg = Message("Password Reset Request", 
                          sender=app.config["MAIL_DEFAULT_SENDER"],
                          recipients=[email])
            # HTML styled email content
            msg.html = f"""
            <html>
            <head>
                <style>
                    .container {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: auto;
                        padding: 20px;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        background-color: #f9f9f9;
                    }}
                    .header {{
                        font-size: 24px;
                        color: #3f9af4;
                        margin-bottom: 20px;
                    }}
                    .message {{
                        font-size: 16px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 25px;
                        margin-top: 20px;
                        background-color: #3f9af4;
                        color: #fff;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                    }}
                    .footer {{
                        font-size: 14px;
                        color: #888;
                        margin-top: 30px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2 class="header">Password Reset Request - WindCloud</h2>
                    <p class="message">Hello,</p>
                    <p class="message">We received a request to reset your password. To update your credentials, please click the button below:</p>
                    <p><a class="button" href="{reset_link}">Reset Password</a></p>
                    <p class="message">If you did not request this, simply ignore this email. Your password remains unchanged.</p>
                    <p class="footer">Best regards,<br>The WindCloud Team</p>
                </div>
            </body>
            </html>
            """
            mail.send(msg)
            flash("Password reset email sent. Please check your email.", "info")
        else:
            flash("Email not found.", "warning")
        return redirect(url_for("login"))
    return render_template("reset_password.html")

# New route: Reset password using token
@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_token(token):
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=3600)
    except SignatureExpired:
        flash("The reset token has expired.", "danger")
        return redirect(url_for("reset_request"))
    except BadSignature:
        flash("Invalid reset token.", "danger")
        return redirect(url_for("reset_request"))
    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("reset_token", token=token))

        # Validate password: at least 8 chars, one uppercase letter, and one digit.
        if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"\d", password):
            flash("Password must be at least 8 characters long, contain at least one uppercase letter and one digit.", "danger")
            return redirect(url_for("reset_token", token=token))

        hashed_pw = hash_password(password)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_pw, email))
        conn.commit()
        flash("Password has been reset. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("new_password.html", token=token)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=False)

