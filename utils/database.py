"""
database.py
------------
Lightweight SQLite storage for prediction history.

Why SQLite: no separate database server needed - it's a single file
(model/history.db) that Python's built-in `sqlite3` module can read
and write directly. Perfect for a beginner-friendly academic project.

Used by:
- app.py            -> saves a row after every successful prediction
- Dashboard page     -> aggregate stats + chart data
- History page       -> full table of past predictions
"""

import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "model", "history.db")


def init_db():
    """Create the predictions table if it doesn't already exist. Safe to call every startup."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            patient_name TEXT,
            age INTEGER,
            gender TEXT,
            symptoms TEXT,
            disease TEXT,
            confidence REAL,
            risk_level TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_prediction(patient_name, age, gender, symptoms, disease, confidence, risk_level, user_id=None):
    """
    Insert one prediction record. `symptoms` should be passed as a
    comma-separated string (SQLite has no native list type).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (user_id, patient_name, age, gender, symptoms, disease, confidence, risk_level, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        patient_name,
        age,
        gender,
        ", ".join(symptoms) if isinstance(symptoms, list) else symptoms,
        disease,
        confidence,
        risk_level,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))
    conn.commit()
    conn.close()


def get_all_predictions(limit=None, user_id=None):
    """Return predictions, most recent first. Optionally limit the count and/or filter to one user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    params = []
    query = "SELECT * FROM predictions"
    if user_id is not None:
        query += " WHERE user_id = ?"
        params.append(user_id)
    query += " ORDER BY id DESC"
    if limit:
        query += " LIMIT ?"
        params.append(int(limit))
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_dashboard_stats(user_id=None):
    """
    Compute aggregate stats used by the Dashboard page:
    - total prediction count
    - disease distribution (for the pie chart)
    - predictions per day, last 7 entries (for the bar chart)

    Pass user_id to scope all stats to just that user's own predictions.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    where_clause = " WHERE user_id = ?" if user_id is not None else ""
    params = [user_id] if user_id is not None else []

    cursor.execute(f"SELECT COUNT(*) as total FROM predictions{where_clause}", params)
    total = cursor.fetchone()["total"]

    cursor.execute(f"""
        SELECT disease, COUNT(*) as count
        FROM predictions{where_clause}
        GROUP BY disease
        ORDER BY count DESC
    """, params)
    disease_distribution = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT substr(created_at, 1, 10) as day, COUNT(*) as count
        FROM predictions{where_clause}
        GROUP BY day
        ORDER BY day DESC
        LIMIT 7
    """, params)
    daily_counts = [dict(row) for row in cursor.fetchall()][::-1]  # chronological order

    conn.close()

    return {
        "total": total,
        "disease_distribution": disease_distribution,
        "daily_counts": daily_counts,
    }
