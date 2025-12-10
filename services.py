import os
import httpx
import asyncio

# Shared constants
API_KEY = os.getenv("OPENWEATHER_API_KEY")

known_cities = [
    "New York", "London", "Tokyo", "Sydney", "Mumbai",
    "Orlando", "Los Angeles", "Miami", "Honolulu",
    "San Francisco", "Washington D.C.", "Chicago",
    "San Diego", "New Orleans", "Denver", "Seattle",
    "Phoenix", "Boston", "Atlanta", "Dallas", "Houston",
    "Nashville", "Austin", "Salt Lake City", "Portland",
    "Charleston", "Philadelphia", "Yosemite National Park", "Cincinnati",
]

airport_codes = {
    "london": "LON",
    "jfk": "JFK",
    "new york": "JFK",
    "tokyo": "TYO",
    "sydney": "SYD",
    "mumbai": "BOM",
    "los angeles": "LAX",
    "miami": "MIA",
    "san francisco": "SFO",
    "orlando": "MCO",
    "cincinnati": "CVG",
}

async def fetch_weather(city: str):
    if not API_KEY:
        raise RuntimeError("OPENWEATHER_API_KEY not set")
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "imperial"}  # returns Fahrenheit in main.temp
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=15.0)
        resp.raise_for_status()
        data = resp.json()
        # ensure a stable field for templates: temp_f (Fahrenheit)
        if "main" in data and "temp" in data["main"]:
            try:
                data["main"]["temp_f"] = float(data["main"]["temp"])
            except Exception:
                data["main"]["temp_f"] = data["main"]["temp"]
        return data

async def fetch_flights_amadeus(origin: str, dest_airport: str):
    # Temporary stub — return sample flights; replace with real API call later.
    sample = [
        {"airline": "Acme Air", "flight_number": "AC102", "departure_time": "08:00", "arrival_time": "20:00", "price": 399.99, "departure_date": ""},
        {"airline": "BudgetFly", "flight_number": "BF550", "departure_time": "09:30", "arrival_time": "22:10", "price": 289.50, "departure_date": ""},
        {"airline": "SkyWays", "flight_number": "SW077", "departure_time": "13:15", "arrival_time": "01:05", "price": 349.00, "departure_date": ""},
    ]
    await asyncio.sleep(0.05)
    return sample