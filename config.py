import os
from dotenv import load_dotenv

load_dotenv()
# Flask Application Configuration

# Security Settings
SECRET_KEY = 'test100'  # Change this to a secure random value in production
SESSION_TYPE = "filesystem"  # Session storage typepip install python-dotenv
SESSION_PERMANENT = False    # Sessions expire when browser closes
SESSION_USE_SIGNER = True  # Signierte Cookies
SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookies
SESSION_COOKIE_SAMESITE = "Lax"  # CSRF protection

# Rate Limiting
RATE_LIMIT = "100 per day"  # API request rate limit per user

# File Upload Settings
UPLOAD_FOLDER = "uploads"  # Directory for storing uploaded files

# Mail configuration from environment variables
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')