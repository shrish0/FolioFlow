from fastapi import FastAPI
from app.api import telegram

app = FastAPI(title="TeleFolio", version="1.0.0")

# Include Telegram webhook router
app.include_router(telegram.router, prefix="/telegram")
