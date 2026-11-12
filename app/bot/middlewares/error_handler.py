import traceback
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery
from app.core.config import settings
from app.core.logging import logger


class GlobalErrorHandlerMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as exc:
            logger.error(f"Global exception in Telegram handler: {exc}", exc_info=True)
            tb = traceback.format_exc()

            # Attempt to inform user kindly
            try:
                if isinstance(event, Message):
                    await event.answer("⚠️ Kechirasiz, tizimda kutilmagan xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("⚠️ Xatolik yuz berdi.", show_alert=True)
            except Exception:
                pass

            # Notify admins
            for admin_id in settings.admin_ids:
                try:
                    alert_text = (
                        f"🚨 <b>Botda kutilmagan xatolik!</b>\n\n"
                        f"<code>{str(exc)[:200]}</code>\n\n"
                        f"<pre>{tb[-500:]}</pre>"
                    )
                    await self.bot.send_message(chat_id=admin_id, text=alert_text, parse_mode="HTML")
                except Exception:
                    pass
            return None
