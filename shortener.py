import sqlite3

# Function for table creation
def create_table():
    db = sqlite3.connect('shortener.db')
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              url TEXT NOT NULL,
              alias TEXT NOT NULL,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    db.commit()
    db.close()

# Function for inserting a url into the table
def insert_url(url, alias):
  conn = sqlite3.connect('shortener.db')
  c = conn.cursor()
  c.execute("INSERT INTO urls (url, alias) VALUES (?, ?)", (url, alias))
  conn.commit()
  conn.close()

# Function for deleting a url
def delete_url(alias):
  conn = sqlite3.connect('shortener.db')
  c = conn.cursor()
  c.execute("DELETE FROM urls WHERE alias=?", (alias,))
  conn.commit()
  conn.close()

# Function for listing all urls
def list_urls():
  conn = sqlite3.connect('shortener.db')
  c = conn.cursor()
  c.execute("SELECT * FROM urls")
  rows = c.fetchall()
  conn.close()
  return rows

# Function for retrieving 1 url based on alias
def get_url(alias):
  conn = sqlite3.connect('shortener.db')
  c = conn.cursor()
  c.execute("SELECT url FROM urls WHERE alias=?", (alias,))
  row = c.fetchone()
  conn.close()
  return row[0] if row else None

# Function for checking if alias exists in the db
def alias_exists(alias):
  conn = sqlite3.connect('shortener.db')
  c = conn.cursor()
  c.execute("SELECT COUNT(*) FROM urls WHERE alias=?", (alias,))
  count = c.fetchone()[0]
  conn.close()
  return count > 0

# Create the table if it doesn't exist
create_table()
