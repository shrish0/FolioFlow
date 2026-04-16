# Architecture Overview

## High‑Level Diagram (textual)

```
+-------------------+        +-------------------+        +-------------------+
|   Telegram Bot   |  <---> |  FastAPI Webhook  |  <---> |   Redis Queue     |
+-------------------+        +-------------------+        +-------------------+
        ^                           ^                         ^
        |                           |                         |
        |                           |                         |
        |                           |                         |
        |                           |                         |
        |                           |                         |
        |                           |                         |
        |                           |                         |
        |                           |                         |
        v                           v                         v
+-------------------+        +-------------------+        +-------------------+
|  python‑telegram‑ |        |  app/services/   |        |  app/core/       |
|  bot (async)      |        |  telegram_service |        |  logger.py       |
+-------------------+        +-------------------+        +-------------------+
```

## Layered Architecture

| Layer | Responsibility | Key Modules |
|-------|----------------|--------------|
| **Presentation** | Exposes HTTP endpoint for Telegram webhook. | `app/api/telegram/router.py` |
| **Application** | Orchestrates request handling, delegates to services. | `app/services/telegram_service.py` |
| **Domain / Service** | Business logic: command parsing, keyword detection, message composition, analytics tracking. | `TelegramService` methods (`_send_start`, `_send_portfolio`, …) |
| **Infrastructure** | Configuration, logging, queue, data access. | `app/core/config.py`, `app/core/logger.py`, `app/core/queue.py`, `app/data/portfolio.py` |
| **External Systems** | Telegram Bot API, Redis, optional AI provider, Render platform. | `python‑telegram‑bot`, `aioredis` |

## Core Flow
1. **Telegram sends an update** to the webhook URL (`/telegram/webhook`).
2. **FastAPI router** receives the POST request and forwards the raw JSON payload to `TelegramService.handle_update`.
3. `TelegramService` **deserialises** the payload into a `telegram.Update` object.
4. Depending on the payload type:
   - **Message** → command (`/start`, `/portfolio`, …) or keyword detection.
   - **CallbackQuery** → button press handling.
5. The appropriate helper builds a **Markdown‑formatted response** and optional **inline keyboard**.
6. The **Bot client** (`Bot(token)`) sends the response back to the user.
7. Every interaction is **logged** via Loguru and **pushed** to a Redis list (`analytics`) for later processing.
8. (Future) A **background worker** can consume the Redis list and store analytics or invoke an LLM for AI‑generated answers.

## Design Decisions
- **Webhook over polling** – reduces latency, scales with Render’s auto‑HTTPS.
- **Async‑first** – all I/O (FastAPI, Telegram Bot, Redis) uses async/await for high concurrency.
- **Clean separation** – routers only expose HTTP; services contain all business rules; core utilities provide cross‑cutting concerns (config, logging, queue).
- **Environment‑driven config** – `pydantic-settings` reads from `.env`; no hard‑coded secrets.
- **Redis queue** – lightweight, non‑blocking analytics; can be swapped for a message broker (e.g., RabbitMQ) later.
- **Placeholder AI** – `_send_fallback` returns a stub message; the method signature is ready for LLM integration without breaking existing code.

## Scalability & Production Readiness
- **Stateless FastAPI** – can be horizontally scaled behind Render’s load balancer.
- **Redis** – single‑node in Render free tier; for higher load upgrade to managed Redis.
- **Log rotation** – Loguru rotates at 10 MB, retains 7 days, preventing disk exhaustion.
- **Health checks** – FastAPI provides `/docs` and `/openapi.json`; Render can ping `/health` if added.
- **CI/CD** – Add GitHub Actions to lint (`ruff`), run tests, and push to Render on merge.

---

*This architecture document is part of the TeleFolio repository and should be kept up‑to‑date as the system evolves.*
