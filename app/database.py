import sqlite3
from typing import List, Dict, Any, Optional
from app.config import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            gemini_api_key TEXT,
            currency_pref TEXT DEFAULT '$',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create recommendations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            budget REAL NOT NULL,
            currency TEXT DEFAULT '$',
            input_params TEXT NOT NULL,
            result_data TEXT NOT NULL,
            image_path TEXT,
            is_favorite INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def seed_demo_user(password_hash: str):
    """Seed a default demo user if no users exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = 'demo@pocketsmart.ai'")
    existing = cursor.fetchone()
    if not existing:
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, full_name, currency_pref)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("demo_user", "demo@pocketsmart.ai", password_hash, "Alex Morgan", "$")
        )
        conn.commit()
    conn.close()
