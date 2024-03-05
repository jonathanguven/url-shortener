import sqlite3
from modules.hash import generate_hash
import logging

def connect():
    print("Connecting to database")
    connection = sqlite3.connect('shortener.db')
    return connection

def alias_exists(alias: str):
    connection = connect()
    c = connection.cursor()
    c.execute("SELECT COUNT(*) FROM urls WHERE alias=?", (alias,))
    count = c.fetchone()[0]
    connection.close()
    return count > 0

def get_url(alias: str):
    connection = connect()
    c = connection.cursor()
    c.execute("SELECT url FROM urls WHERE alias=?", (alias,))
    row = c.fetchone()
    connection.close()
    return row[0]

def create_alias(url: str, alias: str = None):
    if not alias:
        alias = generate_hash(url)
    if alias_exists(alias):
        return None
    else:
        connection = connect()
        c = connection.cursor()
        c.execute("INSERT INTO urls (url, alias) VALUES (?, ?)", (url, alias))
        connection.commit()
        connection.close()
        return alias

def delete_alias(alias: str):
    connection = connect()
    c = connection.cursor()
    try: 
      c.execute("DELETE FROM urls WHERE alias=?", (alias,))
      connection.commit()
      return c.rowcount > 0
    except Exception:
      return False

def list_urls():
    connection = connect()
    c = connection.cursor()
    c.execute("SELECT * FROM urls")
    rows = c.fetchall()
    connection.close()
    return rows