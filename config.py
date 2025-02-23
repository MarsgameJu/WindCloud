import os

# Flask Application Configuration

# Security Settings
SECRET_KEY = 'test100'  # Change this to a secure random value in production
SESSION_TYPE = "filesystem"  # Session storage type
SESSION_PERMANENT = False    # Sessions expire when browser closes
SESSION_USE_SIGNER = True  # Signierte Cookies
SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookies
SESSION_COOKIE_SAMESITE = "Lax"  # CSRF protection

# Rate Limiting
RATE_LIMIT = "100 per day"  # API request rate limit per user

# File Upload Settings
UPLOAD_FOLDER = "uploads"  # Directory for storing uploaded files
