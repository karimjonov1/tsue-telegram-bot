import asyncio
from typing import Optional, Tuple
from aiogram import Bot
from aiogram.types import Message
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError, TelegramAPIError
from sqlalchemy import select

from app.core.models import User
from app.core.db import AsyncSessionLocal
from app.core.logging import logger


async def broadcast_message(
    bot: Bot,
    source_message: Message,
    group_id: Optional[int] = None
) -> Tuple[int, int]:
    """
    Broadcasts a message (text, photo, formatting) to all active users
    or users of a specific group.
    Returns: (sent_count, failed_count)
    """
    async with AsyncSessionLocal() as session:
        query = select(User).where(User.is_active == True)
        if group_id is not None:
            query = query.where(User.selected_group_id == group_id)
        
        res = await session.execute(query)
        users = list(res.scalars().all())

    sent = 0
    failed = 0

    for user in users:
        try:
            await source_message.copy_to(chat_id=user.id)
            sent += 1
        except TelegramRetryAfter as e:
            logger.warning(f"Broadcast rate-limited. Waiting {e.retry_after}s...")
            await asyncio.sleep(e.retry_after)
            try:
                await source_message.copy_to(chat_id=user.id)
                sent += 1
            except Exception:
                failed += 1
        except TelegramForbiddenError:
            # User blocked bot
            failed += 1
            async with AsyncSessionLocal() as session:
                u = await session.get(User, user.id)
                if u:
                    u.is_active = False
                    await session.commit()
        except TelegramAPIError as e:
            logger.error(f"Failed to send broadcast to {user.id}: {e}")
            failed += 1
        except Exception as e:
            logger.error(f"Unexpected error broadcasting to {user.id}: {e}")
            failed += 1

        # Throttle ~25 msgs/sec
        await asyncio.sleep(0.04)

    logger.info(f"Broadcast finished. Sent: {sent}, Failed: {failed}")
    return sent, failed
