Python Backend Developer Portfolio

Dad and newly-minted Python backend developer.
Built 3 serverless microservices in 90 days while fighting for custody of my 5-year-old.

Tech Stack:
Python • FastAPI • AWS (Lambda, API Gateway, DynamoDB, S3) • Render
OpenAI • ElevenLabs • HTML/CSS/Vanilla JS

This repository showcases real, working APIs — not tutorials — with live demos and cloud deployments.

🧰 Projects Overview
Project	Status	Deployment
Toshi-chan Currency Converter	v1 Live	Render + AWS Elastic Beanstalk
Cloudy Weather Dashboard API	v1 Live	Render
Link Shortener API	v1 (Render-ready)	Local / Deployable

💱 Toshi-chan Currency Converter (v1)

Live Demo:
👉 https://dad-dev-toolkit.onrender.com/

A playful but production-minded API that converts USD → JPY, calculates a custom “Toshi-coin” value, and generates a flirty AI response.

Core Features

USD → JPY conversion

Custom Toshi-coin calculation

AI-generated commentary (OpenAI GPT-4o-mini)

Optional text-to-speech via ElevenLabs (disabled in v1)

Tech Stack

FastAPI

OpenAI GPT-4o-mini

CoinGecko API

HTML / CSS / Vanilla JS

Render + AWS Elastic Beanstalk

Status

✅ Deployed and tested on AWS Elastic Beanstalk

✅ Live demo running on Render

🔜 v2 roadmap: voice playback re-enabled, expanded AI responses

Elastic Beanstalk Deployment Structure
toshi-api/
├─ app.py
├─ Procfile
├─ requirements.txt
├─ runtime.txt
├─ .env.example
├─ static/
│  ├─ main.js
│  ├─ styles.css
│  └─ toshi-cat.png
└─ templates/
   └─ index.html

☁️ Cloudy Weather Dashboard API (v1)

Live Demo:
👉 https://cloudy-api-v1.onrender.com/

A FastAPI-based weather dashboard that displays real-time conditions with dynamic background videos hosted on a separate Render static site.

Features

Real-time weather data via WeatherAPI

Temperature, wind speed, conditions

Dynamic video backgrounds:

Clear → Clear.mp4

Cloudy → Cloudy.mp4

Rainy → Rainy.mp4

Snowy → Snowy.mp4

Sunny → Sunny.mp4

Responsive UI using FastAPI + Jinja2

Tech Stack

Python

FastAPI

Jinja2

HTTPX

Render (API + static video hosting)

Notes

v1 only: UI includes a flight search bar placeholder (non-functional)

Flight search functionality planned for v2

🔗 Link Shortener API (v1)

Status: ✅ Render-ready (not deployed yet)

A lightweight URL shortener built as an MVP foundation for future monetization and scaling.

This service is intentionally not deployed to avoid Render conflicts in a multi-project portfolio repo.
Code is production-ready and deployable without changes.

Features

Shorten long URLs

Instant redirects

Minimal HTML/JS frontend

FastAPI backend

Clean MVP architecture

⚠️ IMPORTANT URL REQUIREMENT

All URLs must include a protocol:

✅ https://example.com
❌ example.com

(Frontend auto-fix planned for v2)

Tech Stack

FastAPI

Uvicorn

HTML / CSS / Vanilla JS

Python 3.13+

API Endpoints

Create Short Link

POST /shorten
{
  "url": "https://example.com"
}


Redirect

GET /{short_id}

v2 Roadmap

Custom vanity URLs (paid)

Persistent database

Click analytics

Authentication

Rate limiting

Stripe integration

🧪 Running Locally
pip install -r requirements.txt
uvicorn main:app --reload


Open: http://127.0.0.1:8000

🔐 Environment Variables

Toshi API

OPENAI_API_KEY

ELEVENLABS_API_KEY (optional)

ELEVEN_VOICE_ID (optional)

Cloudy API

WEATHERAPI_KEY

📁 Repository Structure
Dad-dev-toolkit/
├─ toshi-api/
├─ cloudy-weather/
├─ link-shortener/
└─ README.md

🎯 Final Recruiter Note

This portfolio focuses on:

Real APIs

Real deployments

Real debugging

Real constraints

No tutorials. No placeholders. Just shipping.
