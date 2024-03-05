from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
import uvicorn
import logging
import time

from modules.args import get_args
from modules.helper import connect, alias_exists, get_url, create_alias, delete_alias, list_urls

app = FastAPI()
router = APIRouter()
args = get_args()

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
    alias = create_alias(url, alias)
    if alias is None:
        raise HTTPException(status_code=400, detail="Alias already exists. Please enter different alias.")
    else:
        return {"message": f"URL for {alias} inserted successfully"}

@app.delete("/delete/{alias}")
async def delete_url(alias: str):
    if delete_alias(alias):
        return {"message": f"URL for {alias} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Alias not found")

@app.get("/list")
async def list_urls_endpoint():
    return list_urls()

@app.get("/find/{alias}")
async def find(alias: str):
    if alias_exists(alias):
        url = get_url(alias)
        return RedirectResponse(url)
    else:
        raise HTTPException(status_code=404, detail="Alias not found")

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