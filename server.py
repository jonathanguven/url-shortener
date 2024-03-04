from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
import sqlite3
import uvicorn
import logging
import time

from modules.hash import generate_hash
from modules.args import get_args


app = FastAPI()
router = APIRouter()
args = get_args()

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
    alias = data.get('alias', None)
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

@app.get("/list")
async def list_urls():
    connection = connect()
    c = connection.cursor()
    c.execute("SELECT * FROM urls")
    rows = c.fetchall()
    connection.close()
    return rows

@app.get("/find/{alias}")
async def find(alias: str):
    if alias_exists(alias):
        url = get_url(alias)
        return RedirectResponse(url)
    else:
        raise HTTPException(status_code=404, detail="Alias not found")

@app.get("/")
def root():
    return "url-shortener"

@app.get("/logging-levels")
def logging_levels():
    logging.error("This is an error message")
    logging.warning("This is a warning message")
    logging.info("This is an info message")
    logging.debug("This is a debug message")
logging.Formatter.converter = time.gmtime
logging.basicConfig(
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level= logging.ERROR - (args.verbose*10),
)

if __name__ == "__main__":
    uvicorn.run("server:app", host=args.host, port=args.port, reload=True)