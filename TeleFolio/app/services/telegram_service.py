# app/services/telegram_service.py
"""Telegram bot service handling incoming updates and sending responses.
Implements command handling, keyword detection, and inline keyboard navigation.
Uses python-telegram-bot (async) client.
"""

import os
from typing import Any, Dict, List

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError

from app.core.config import settings
from app.core.logger import analytics_logger
from app.core.queue import analytics_queue
from app.data.portfolio import get_portfolio_projects, get_skills, get_resume_link, get_contact_info

# Initialize the async Bot instance (singleton)
_bot = Bot(token=settings.telegram_bot_token)

class TelegramService:
    """High‑level service that processes Telegram webhook payloads.

    The FastAPI router passes the raw JSON payload to ``handle_update``.
    ``handle_update`` parses the payload into a ``telegram.Update`` object,
    determines the appropriate action, and sends a response using the async Bot.
    """

    @staticmethod
    async def handle_update(payload: Dict[str, Any]) -> None:
        """Entry point called from the FastAPI webhook.

        Args:
            payload: The JSON body received from Telegram.
        """
        update = Update.de_json(payload, _bot=_bot)
        # Log analytics (user_id, command/keyword, timestamp)
        await TelegramService._track_interaction(update)

        if update.message:
            await TelegramService._handle_message(update)
        elif update.callback_query:
            await TelegramService._handle_callback(update)
        else:
            # Unsupported update type – ignore
            return

    @staticmethod
    async def _track_interaction(update: Update) -> None:
        """Push a lightweight analytics record to Redis queue.
        The record format is a simple dict; a background worker can later
        persist it to a DB or log file.
        """
        user_id = update.effective_user.id if update.effective_user else None
        command = (
            update.message.text if update.message else update.callback_query.data
        )
        record = {"user_id": user_id, "command": command}
        # Fire‑and‑forget push to Redis list
        await analytics_queue.rpush("analytics", str(record))
        analytics_logger.info(f"Tracked interaction: {record}")

    @staticmethod
    async def _handle_message(update: Update) -> None:
        """Process plain text messages and commands.
        Supports both ``/command`` style and keyword detection.
        """
        text = update.message.text.strip()
        chat_id = update.effective_chat.id

        if text.startswith('/'):
            # Command handling
            command = text.split()[0].lower()
            if command == "/start":
                await TelegramService._send_start(chat_id)
            elif command == "/portfolio":
                await TelegramService._send_portfolio(chat_id)
            elif command == "/skills":
                await TelegramService._send_skills(chat_id)
            elif command == "/resume":
                await TelegramService._send_resume(chat_id)
            elif command == "/contact":
                await TelegramService._send_contact(chat_id)
            else:
                await TelegramService._send_unknown(chat_id)
        else:
            # Keyword detection (case‑insensitive)
            lowered = text.lower()
            if "project" in lowered:
                await TelegramService._send_portfolio(chat_id)
            elif "skill" in lowered:
                await TelegramService._send_skills(chat_id)
            elif "resume" in lowered:
                await TelegramService._send_resume(chat_id)
            elif "contact" in lowered or "email" in lowered:
                await TelegramService._send_contact(chat_id)
            else:
                await TelegramService._send_fallback(chat_id, text)

    @staticmethod
    async def _handle_callback(update: Update) -> None:
        """Handle button presses from inline keyboards.
        The ``callback_data`` is used to route to the same helper methods.
        """
        query = update.callback_query
        await query.answer()  # Acknowledge the button press
        data = query.data
        chat_id = query.message.chat.id

        if data == "portfolio":
            await TelegramService._send_portfolio(chat_id)
        elif data == "skills":
            await TelegramService._send_skills(chat_id)
        elif data == "resume":
            await TelegramService._send_resume(chat_id)
        elif data == "contact":
            await TelegramService._send_contact(chat_id)
        else:
            await TelegramService._send_unknown(chat_id)

    # ---------------------------------------------------------------------
    # Helper methods that build messages and keyboards
    # ---------------------------------------------------------------------
    @staticmethod
    async def _send_start(chat_id: int) -> None:
        text = (
            "👋 *Welcome to TeleFolio!*\n\n"
            "I can show you my portfolio, skills, resume and contact info.\n"
            "Use the buttons below or type commands like /portfolio, /skills, /resume, /contact."
        )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Portfolio", callback_data="portfolio"),
                    InlineKeyboardButton("Skills", callback_data="skills"),
                ],
                [
                    InlineKeyboardButton("Resume", callback_data="resume"),
                    InlineKeyboardButton("Contact", callback_data="contact"),
                ],
            ]
        )
        await _bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

    @staticmethod
    async def _send_portfolio(chat_id: int) -> None:
        projects = get_portfolio_projects()
        if not projects:
            await _bot.send_message(chat_id, "No projects found.")
            return
        lines = []
        for p in projects:
            lines.append(
                f"*{p['name']}*\n{p['description']}\n*Tech*: {', '.join(p['tech_stack'])}\n[GitHub]({p['github']})\n"
            )
        text = "\n---\n".join(lines)
        await _bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    @staticmethod
    async def _send_skills(chat_id: int) -> None:
        skills = get_skills()
        await _bot.send_message(
            chat_id,
            "*Technical Skills:*\n" + ", ".join(skills),
            parse_mode=ParseMode.MARKDOWN,
        )

    @staticmethod
    async def _send_resume(chat_id: int) -> None:
        link = get_resume_link()
        await _bot.send_message(
            chat_id,
            f"Here is my resume: [View]({link})",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )

    @staticmethod
    async def _send_contact(chat_id: int) -> None:
        info = get_contact_info()
        await _bot.send_message(
            chat_id,
            f"*Email*: {info['email']}\n*LinkedIn*: {info['linkedin']}",
            parse_mode=ParseMode.MARKDOWN,
        )

    @staticmethod
    async def _send_unknown(chat_id: int) -> None:
        await _bot.send_message(chat_id, "Sorry, I didn't understand that command.")

    @staticmethod
    async def _send_fallback(chat_id: int, original_text: str) -> None:
        # Placeholder for future LLM integration
        await _bot.send_message(
            chat_id,
            f"I received: '{original_text}'. I will add AI‑powered answers later!",
        )
"
