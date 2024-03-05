from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
import uvicorn
import logging
import time

from modules.args import get_args
from modules.hash import generate_hash
from modules.helper import alias_exists, get_url, create_alias, delete_alias, list_urls, create_table

app = FastAPI()
args = get_args()

DB_PATH = "shortener.db"

create_table('shortener.db')

@app.post("/create_url")
async def create_url(request: Request):
    data = await request.json()
    alias = data.get('alias', None)
    if alias is None:
        alias = generate_hash(data['url'])

    response = create_alias(DB_PATH, data['url'], alias)
    if response is not None:
        return { "url": data['url'], "alias": alias, "created_at": response}
    else:
        raise HTTPException(status_code=500, detail="Alias already exists. Please choose another one.")
    
@app.delete("/delete/{alias}")
async def delete_url(alias: str):
    if delete_alias(DB_PATH, alias):
        return {"message": f"URL for {alias} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Alias not found")

@app.get("/list")
async def list_urls_endpoint():
    return list_urls(DB_PATH)

@app.get("/find/{alias}")
async def find(alias: str):
    if alias_exists(DB_PATH, alias):
        url = get_url(DB_PATH, alias)
        return RedirectResponse(url)
    else:
        raise HTTPException(status_code=404, detail="Alias not found")

@app.get("/logging")
def logging_levels():
    logging.error("error message")
    logging.warning("warning message")
    logging.info("info message")
    logging.debug("debug message")

logging.Formatter.converter = time.gmtime
logging.basicConfig(
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level= logging.ERROR - (args.verbose*10),
)

if __name__ == "__main__":
    logging.info(f"running on {args.host}, listening on port {args.port}")
    uvicorn.run("server:app", host=args.host, port=args.port, reload=True)