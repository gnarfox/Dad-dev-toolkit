import os
from datetime import datetime
import urllib.parse
import httpx
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

load_dotenv()

# -------------------------------
# FastAPI app + Static Files
# -------------------------------
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# -------------------------------
# Known Cities List
# -------------------------------
known_cities = [
    "New York", "London", "Paris", "Tokyo", "Sydney", "Mumbai",
    "Cairo", "Rio de Janeiro", "Moscow", "Toronto", "Los Angeles",
    "Chicago", "Houston", "Miami", "Berlin", "Madrid", "Rome",
    "Beijing", "Seoul", "Bangkok", "Cincinnati", "Columbus",
    "Cleveland", "San Francisco", "Seattle", "Phoenix", "Denver", "Orlando",
    "Austin", "Nashville", "Salt Lake City", "Portland", "Charleston",
    "Philadelphia", "Yosemite National Park", "Thornville, Ohio", "West Chester, Ohio", "Cancun, Mexico"
]

# -------------------------------
# Background Video Selector
# -------------------------------
def choose_background(condition: str):
    c = condition.lower()

    if "clear" in c:
        return "clear.mp4"
    elif "snow" in c or "freezing" in c:
        return "snowy.mp4"
    elif "rain" in c or "drizzle" in c:
        return "rainy.mp4"
    elif "cloud" in c or "overcast" in c:
        return "cloudy.mp4"
    
    return "sunny.mp4"  # fallback


# -------------------------------
# WeatherAPI Fetcher  (NEW!)
# -------------------------------
async def fetch_weather(city: str):
    """
    Fetches weather data from WeatherAPI.com and normalizes
    the fields so the HTML template doesn't need to change.
    """
    API_KEY = os.getenv("WEATHERAPI_KEY")
    if not API_KEY:
        raise RuntimeError("Missing WEATHERAPI_KEY environment variable!")

    url = "https://api.weatherapi.com/v1/current.json"
    params = {"key": API_KEY, "q": city}

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        # --- Normalize data to match OpenWeather format ---
        normalized = {
            "main": {
                "temp_f": data["current"]["temp_f"]
            },
            "weather": [
                {"description": data["current"]["condition"]["text"]}
            ],
            "wind": {
                "speed": data["current"]["wind_mph"]
            }
        }

        return normalized


# -------------------------------
# Root Route
# -------------------------------
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "cities": known_cities}
    )


# -------------------------------
# Weather Page
# -------------------------------
@app.get("/weather/{city}", response_class=HTMLResponse)
async def get_weather(request: Request, city: str):

    # Decode URL like Los%20Angeles → Los Angeles
    city_decoded = urllib.parse.unquote_plus(city).strip()

    # Find matching known city (case-insensitive)
    matched = next(
        (c for c in known_cities if c.lower() == city_decoded.lower()),
        None
    )

    if not matched:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": f"City not found: {city_decoded}"}
        )

    # Fetch weather from WeatherAPI
    try:
        weather = await fetch_weather(matched)
        condition = weather["weather"][0]["description"]
        background = choose_background(condition)

    except Exception as e:
        print("WeatherAPI error:", e)
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Failed to fetch weather."}
        )

    return templates.TemplateResponse(
        "weather.html",
        {
            "request": request,
            "city": matched,
            "weather": weather,
            "background": background,
            "timestamp": datetime.now().timestamp()
        }
    )
