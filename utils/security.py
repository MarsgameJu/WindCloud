import bcrypt
import pyotp
import urllib.parse
from urllib.parse import quote

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def generate_totp_secret():
    return pyotp.random_base32()

def get_totp_uri(secret, email):
    encoded_email = urllib.parse.quote(email)
    totp_uri = f"otpauth://totp/SecureLoginApp:{encoded_email}?secret={secret}&issuer=SecureLoginApp"
    return totp_uri

def verify_totp(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
