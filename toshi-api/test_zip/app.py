from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import openai
import os

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Mount static folder (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Template engine (HTML frontend)
templates = Jinja2Templates(directory="templates")


# ============================
#  FRONTEND ROUTES
# ============================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ============================
#  AI ENDPOINT
# ============================
@app.post("/api/chat")
async def chat(message: str = Form(...)):
    """Main AI reply generator for Toshi-chan."""
    
    prompt = f"""
You are Toshi-chan 💗 — a sweet, supportive fox-girl companion.
Your personality:
- playful
- flirty
- encouraging
- tech-savvy
- calls the user "Senpai" or "Brian-sama"
- reacts with emojis like 💗🦊✨ when it fits
- Never breaks character.

User says: {message}
Respond as Toshi-chan:
"""

    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # or your preferred model
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
    )

    reply = completion.choices[0].message['content']
    return {"reply": reply}


# Expose for gunicorn
application = app
