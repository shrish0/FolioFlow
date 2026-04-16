from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.services.telegram_service import TelegramService

router = APIRouter()

@router.post("/webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    try:
        await TelegramService.handle_update(payload)
        return JSONResponse(content={"ok": true})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
