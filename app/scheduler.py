import asyncio
from datetime import datetime, date
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.models import ChatLink, Group
from app.core.db import AsyncSessionLocal
from app.core.logging import logger
from app.services.reminders import check_and_send_reminders
from app.services.backup import create_and_send_backup
from app.services.sync import diff_and_sync_timetable
from app.providers.tsue_seeded import TSUEImageSeededProvider
from app.services.timetable import get_lessons_for_day, format_day_schedule_text


async def morning_chat_post_job(bot: Bot) -> None:
    """Check if any linked group chats should receive today's timetable right now."""
    current_hh_mm = datetime.now().strftime("%H:%M")
    today = date.today()

    async with AsyncSessionLocal() as session:
        query = (
            select(ChatLink)
            .where(
                ChatLink.is_active == True,
                ChatLink.auto_post_time == current_hh_mm
            )
            .options(selectinload(ChatLink.group))
        )
        res = await session.execute(query)
        links = list(res.scalars().all())

    for link in links:
        try:
            lessons, week_type = await get_lessons_for_day(link.group_id, today)
            text = format_day_schedule_text(
                group_name=link.group.name,
                target_date=today,
                lessons=lessons,
                week_type=week_type,
                is_tomorrow=False
            )
            await bot.send_message(
                chat_id=link.chat_id,
                text=f"🌅 <b>Xayrli tong! Bugungi dars jadvali:</b>\n\n{text}",
                parse_mode="HTML"
            )
            logger.info(f"Daily timetable posted to chat {link.chat_id} ({link.title})")
        except Exception as e:
            logger.error(f"Failed to post daily timetable to chat {link.chat_id}: {e}")
        await asyncio.sleep(0.05)


async def daily_backup_job(bot: Bot) -> None:
    """Run daily SQLite online backup and notify first admin."""
    logger.info("Starting daily automated backup job...")
    if settings.admin_ids:
        try:
            await create_and_send_backup(bot, settings.admin_ids[0])
            logger.info("Daily backup job completed and sent to admin.")
        except Exception as e:
            logger.error(f"Daily backup job failed: {e}")


async def sync_timetable_job(bot: Bot) -> None:
    """Run periodic sync and diff to catch any updates."""
    logger.info("Running automated timetable sync job...")
    provider = TSUEImageSeededProvider()
    try:
        res = await diff_and_sync_timetable(provider, bot=bot)
        logger.info(f"Timetable sync finished: {res}")
    except Exception as e:
        logger.error(f"Timetable sync failed: {e}")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Configure APScheduler with all cron and interval jobs."""
    scheduler = AsyncIOScheduler()

    # 1. Reminders every 60 seconds
    scheduler.add_job(
        check_and_send_reminders,
        trigger=IntervalTrigger(seconds=60),
        args=[bot],
        id="lesson_reminders",
        replace_existing=True
    )

    # 2. Morning chat post every 60 seconds (checks current minute)
    scheduler.add_job(
        morning_chat_post_job,
        trigger=IntervalTrigger(seconds=60),
        args=[bot],
        id="morning_chat_post",
        replace_existing=True
    )

    # 3. Daily backup at 03:00 AM
    scheduler.add_job(
        daily_backup_job,
        trigger=CronTrigger(hour=3, minute=0),
        args=[bot],
        id="daily_backup",
        replace_existing=True
    )

    # 4. Hourly sync job
    scheduler.add_job(
        sync_timetable_job,
        trigger=CronTrigger(minute=15),
        args=[bot],
        id="hourly_sync",
        replace_existing=True
    )

    return scheduler
