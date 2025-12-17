from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid

app = FastAPI()

# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

links = {}

class ShortenRequest(BaseModel):
    url: str

@app.post("/shorten")
def shorten(req: ShortenRequest):
    # normalize URL: strip whitespace and ensure http scheme
    raw = req.url.strip()
    if not raw.lower().startswith(("http://", "https://")):
        normalized = "https://" + raw
    else:
        normalized = raw
    short_id = str(uuid.uuid4())[:6]
    links[short_id] = normalized
    print(f"DEBUG: created short_id={short_id} -> {normalized}")
    return {"short_url": f"http://127.0.0.1:8000/{short_id}"}


@app.get("/{short_id}")
def redirect(short_id: str):
    if short_id not in links:
        raise HTTPException(status_code=404, detail="Not found")

    long_url = links[short_id]
    print(f"DEBUG: redirecting {short_id} -> {long_url}")
    return RedirectResponse(url=long_url, status_code=302)
