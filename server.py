from fastapi import FastAPI, APIRouter, HTTPException, Request
import sqlite3
import uvicorn
from hash import generate_hash

app = FastAPI()
router = APIRouter()

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

async def start():
    connection = connect()
    c = connection.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              url TEXT NOT NULL,
              alias TEXT NOT NULL,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    connection.commit()
    connection.close()

router.add_event_handler("startup", start)
app.include_router(router)

@app.post("/create_url")
async def create_url(request: Request):
    data = await request.json()
    url = data.get('url')
    alias = data.get('alias')
    alias = generate_hash(url, alias)
    if alias_exists(alias):
        raise HTTPException(status_code=400, detail="Alias already exists. Please enter different alias.")
    else:
        connection = connect()
        c = connection.cursor()
        c.execute("INSERT INTO urls (url, alias) VALUES (?, ?)", (url, alias))
        connection.commit()
        connection.close()
        return {"message": f"URL for {alias} inserted successfully"}

@app.delete("/delete/{alias}")
async def delete_url(alias: str):
    connection = connect()
    c = connection.cursor()
    c.execute("DELETE FROM urls WHERE alias=?", (alias,))
    connection.commit()
    connection.close()
    return {"message": f"URL for {alias} deleted successfully"}

@app.get("/list_all")
async def list_urls():
    connection = connect()
    c = connection.cursor()
    c.execute("SELECT * FROM urls")
    rows = c.fetchall()
    connection.close()
    return rows

@app.get("/find/{alias}")
async def find(alias: str):
    connection = connect()
    c = connection.cursor()
    c.execute("SELECT url FROM urls WHERE alias=?", (alias,))
    row = c.fetchone()
    connection.close()
    if row:
        return {"url": row[0]}
    else:
        raise HTTPException(status_code=404, detail="Alias not found")


@app.get("/")
def root():
    return "url-shortener"

if __name__ == "__main__":
    uvicorn.run("server:app", port=5000, reload=True)