import sqlite3
import os
import sys
from typing import Dict, Any, List, Optional
from core.path_helper import get_db_path

DB_PATH = get_db_path()

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                keyword TEXT,
                structure_used TEXT,
                phone_number TEXT,
                whatsapp_link TEXT,
                published_url TEXT,
                status TEXT,
                error_message TEXT
            )
        """)
        conn.commit()

def get_setting(key: str, default: str = "") -> str:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

def set_setting(key: str, value: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))
        conn.commit()

def get_all_settings() -> Dict[str, str]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        rows = cursor.fetchall()
        return {row["key"]: row["value"] for row in rows}

def save_settings(settings_dict: Dict[str, str]):
    with get_connection() as conn:
        cursor = conn.cursor()
        for k, v in settings_dict.items():
            cursor.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (k, v))
        conn.commit()

def add_task_history(
    keyword: str,
    structure_used: str,
    phone_number: str = "",
    whatsapp_link: str = "",
    published_url: str = "",
    status: str = "COMPLETED",
    error_message: str = ""
) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO task_history (keyword, structure_used, phone_number, whatsapp_link, published_url, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (keyword, structure_used, phone_number, whatsapp_link, published_url, status, error_message))
        conn.commit()
        return cursor.lastrowid

def get_task_history(limit: int = 50) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM task_history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# Initialize DB when module loaded
init_db()
