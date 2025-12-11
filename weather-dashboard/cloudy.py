from fastapi import APIRouter, Query
from openai import OpenAI
import os

from services import fetch_weather, fetch_flights_amadeus

router = APIRouter()

# don't raise at import-time — allow app to run without an API key
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

@router.get("/cloudy/flight-insight")
async def cloudy_flight_insight(
    origin: str = Query(...),
    destination: str = Query(...),
    date: str = Query(None),
):
    weather = await fetch_weather(destination)
    flights = await fetch_flights_amadeus(origin, destination)

    # If no OpenAI key, return data with a notice instead of throwing
    if client is None:
        return {"weather": weather, "flights": flights, "ai_insight": "OPENAI_API_KEY not configured."}

    ai_insight = None
    try:
        # safe AI call (adjust to your OpenAI client usage)
        ai = client.chat.completions.create(
            model="gpt-5.1-mini",
            messages=[
                {"role": "system", "content": "You are Cloudy, a concise travel+weather assistant."},
                {"role": "user", "content": f"Destination weather: {weather}\nFlights: {flights}\nDate: {date}\nProvide a short insight."}
            ],
        )
        # adapt to your SDK response shape
        ai_insight = getattr(ai.choices[0].message, "content", None) or ai.choices[0].message.content
    except Exception as e:
        ai_insight = f"AI error: {e}"

    return {"weather": weather, "flights": flights, "ai_insight": ai_insight}