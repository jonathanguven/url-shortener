import sqlite3
from datetime import datetime, timedelta
import logging


# only create if not exists
def create_table(sqlite: str) -> bool:
    db = sqlite3.connect(sqlite)
    c = db.cursor()

    try:
        c.execute('''CREATE TABLE IF NOT EXISTS urls
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  url TEXT NOT NULL,
                  alias TEXT NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        db.commit()
        return True
    except Exception:
        return False

def alias_exists(sqlite: str, alias: str):
    db = sqlite3.connect(sqlite)
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM urls WHERE alias=?", (alias,))
    count = c.fetchone()[0]
    return count > 0

def get_url(sqlite: str, alias: str):
    db = sqlite3.connect(sqlite)
    c = db.cursor()
    c.execute("SELECT url FROM urls WHERE alias=?", (alias,))
    row = c.fetchone()
    return row[0]

def create_alias(sqlite: str, url: str, alias: str = None):
    db = sqlite3.connect(sqlite)
    c = db.cursor()
    timestamp = datetime.now()
    if alias_exists('shortener.db', alias):
        return None
    try:
        c.execute("INSERT INTO urls (url, alias, timestamp) VALUES (?, ?, ?)", (url, alias, timestamp))
        db.commit()
        return timestamp
    except Exception:
        return None

def delete_alias(sqlite: str, alias: str):
    db = sqlite3.connect(sqlite)
    cursor = db.cursor()

    try:
        sql = "DELETE FROM urls WHERE alias = ?"
        cursor.execute(sql, (alias, ))
        db.commit()
        return cursor.rowcount > 0
    except Exception:
        return False

def list_urls(sqlite: str):
    db = sqlite3.connect(sqlite)
    c = db.cursor()
    c.execute("SELECT * FROM urls")
    rows = c.fetchall()
    return rows