# TeleFolio

## Overview

**TeleFolio** is a production‑ready Telegram bot built with **FastAPI** that serves as a personal portfolio assistant.  Users interact with the bot to discover:
- Projects
- Technical skills
- Resume link
- Contact information

The bot uses **webhooks** (no polling) for low‑latency, scalable communication and follows a clean‑architecture pattern (routers, services, core, config).  It is ready for deployment on **Render** and includes optional Redis‑based analytics and background‑processing scaffolding for future AI integration.

---

## Features

| Feature | Description |
|--------|-------------|
| `/start` | Intro message with inline keyboard navigation |
| `/portfolio` | Lists projects (name, description, tech stack, GitHub link) |
| `/skills` | Shows a comma‑separated list of technical skills |
| `/resume` | Sends a link (or file) to the resume |
| `/contact` | Returns email and LinkedIn profile |
| Keyword handling | Detects words like *project*, *skill*, *resume*, *contact* in free‑text messages |
| Inline keyboards | Enables button‑based navigation without typing commands |
| Redis queue | Pushes a lightweight analytics record for each interaction |
| Loguru logger | Rotating file logger (`logs/analytics.log`) for audit trails |
| AI placeholder | Stub method ready for future LLM response generation |

---

## Tech Stack

- **Python 3.12**
- **FastAPI** (async) – API gateway and webhook endpoint
- **python‑telegram‑bot[async]** – Telegram Bot API client
- **Pydantic Settings** – Environment‑based configuration (`.env`)
- **Redis (aioredis)** – Queue for analytics / background jobs
- **Loguru** – Structured logging
- **Render** – Cloud platform for deployment (Docker‑free, auto‑HTTPS)

---

## Project Structure

```
TeleFolio/
├─ app/
│  ├─ __init__.py
│  ├─ main.py                     # FastAPI entry point
│  ├─ core/
│  │   ├─ __init__.py
│  │   ├─ config.py               # Pydantic Settings
│  │   ├─ logger.py               # Loguru analytics logger
│  │   └─ queue.py                # Redis queue wrapper
│  ├─ api/
│  │   ├─ __init__.py
│  │   └─ telegram/
│  │       ├─ __init__.py
│  │       ├─ router.py           # /telegram/webhook endpoint
│  └─ services/
│      ├─ __init__.py
│      └─ telegram_service.py     # Business logic, command handling
├─ data/                           # Static JSON data (projects, skills, …)
│   ├─ projects.json
│   ├─ skills.json
│   ├─ resume.json
│   └─ contact.json
├─ logs/                           # Runtime log files (auto‑created)
├─ .env.example                    # Template for environment variables
├─ requirements.txt
├─ README.md
└─ architecture.md                 # High‑level design description
```

---

## Setup & Development

1. **Clone the repository** (already done in your workspace).
2. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure environment variables**:
   - Copy `.env.example` to `.env`.
   - Fill in `TELEGRAM_BOT_TOKEN`, `WEBHOOK_URL`, and `REDIS_URL`.
4. **Run locally** (auto‑reload for development):
   ```bash
   uvicorn app.main:app --reload
   ```
   FastAPI will be available at `http://127.0.0.1:8000`.
5. **Set the Telegram webhook** (replace `<TOKEN>` and `<URL>`):
   ```bash
   curl https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=<WEBHOOK_URL>
   ```
6. **Test** – send `/start` to your bot; you should receive the intro with inline buttons.

---

## Deployment on Render

1. **Create a new Web Service** on Render and connect it to this repository.
2. **Add environment variables** in the Render dashboard (`TELEGRAM_BOT_TOKEN`, `WEBHOOK_URL`, `REDIS_URL`).
3. **Add a `render.yaml`** (included in the repo) – Render will automatically detect it.
4. **Start command** (Render default):
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. **After the service is live**, run the webhook registration command (step 5 above) using the Render URL.
6. **Logs** – Render streams `stdout`; the Loguru file logger writes to `logs/analytics.log` inside the container (persisted via Render’s filesystem).

---

## Extensibility & Future Work

- **AI response module** – Replace the placeholder in `TelegramService._send_fallback` with a call to an LLM (e.g., OpenAI, Gemini) for natural‑language answers.
- **Database integration** – Swap the static JSON files for a proper PostgreSQL or MongoDB store; the repository pattern already exists in the FastAPI template.
- **Background worker** – Spin up a separate Render worker that consumes the Redis `analytics` list and writes aggregated metrics to a data warehouse.
- **Testing suite** – Expand the existing pytest fixtures to cover webhook handling, command routing, and Redis interactions.

---

## License

MIT – feel free to fork, adapt, and showcase this project in your portfolio.
