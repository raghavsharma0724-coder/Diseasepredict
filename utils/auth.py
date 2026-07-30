"""
auth.py
-------
Lightweight username/password authentication backed by the same
SQLite database used for prediction history (model/history.db).

Passwords are never stored in plain text - werkzeug's
generate_password_hash / check_password_hash (salted hashing) is used.

Used by:
- app.py -> /signup, /login, /logout routes + @login_required decorator
"""

import os
import sqlite3
from functools import wraps

from flask import session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "model", "history.db")


def init_users_table():
    """Create the users table if it doesn't already exist. Safe to call every startup."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Add a user_id column to predictions if it doesn't exist yet, so each
    # user's history/dashboard can be filtered to just their own records.
    # (Older history.db files created before login was added won't have it.)
    cursor.execute("PRAGMA table_info(predictions)")
    columns = [row[1] for row in cursor.fetchall()]
    if "user_id" not in columns:
        cursor.execute("ALTER TABLE predictions ADD COLUMN user_id INTEGER")
        conn.commit()

    conn.close()


def create_user(username, password):
    """
    Create a new user with a securely hashed password.
    Returns (True, None) on success, or (False, error_message) if the
    username is already taken.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "That username is already taken."
    finally:
        conn.close()


def verify_user(username, password):
    """
    Check username/password against the stored hash.
    Returns the user's (id, username) tuple on success, or None on failure.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password_hash"], password):
        return {"id": user["id"], "username": user["username"]}
    return None


def login_required(view_func):
    """
    Route decorator - redirects to the login page (preserving the
    originally requested page via ?next=) if no user is logged in.
    """
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.")
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped
