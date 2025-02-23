import sqlite3


def get_db():
    conn = sqlite3.connect("database/users.db")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            totp_secret TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()
