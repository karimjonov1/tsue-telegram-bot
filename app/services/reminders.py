import asyncio
from datetime import datetime, date, timedelta
from typing import List, Optional
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError, TelegramAPIError
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.models import User, Lesson, SentReminder
from app.core.db import AsyncSessionLocal
from app.core.logging import logger
from app.services.timetable import get_week_info
from app.bot.i18n.uz import t


async def check_and_send_reminders(bot: Bot) -> None:
    """
    Periodic job that checks lessons starting in the next ~10 minutes,
    finds subscribed users, and sends alert messages with rate-limiting.
    """
    now = datetime.now()
    today_date = now.date()
    weekday = today_date.isoweekday()
    if weekday > 6:
        return  # Sunday

    current_week_type, _ = get_week_info(today_date)
    today_str = today_date.strftime("%Y-%m-%d")

    async with AsyncSessionLocal() as session:
        # Find all active users with reminders enabled who have a selected group
        query = (
            select(User)
            .where(
                User.is_active == True,
                User.reminders_enabled == True,
                User.selected_group_id.isnot(None)
            )
            .options(selectinload(User.selected_group))
        )
        res = await session.execute(query)
        users = list(res.scalars().all())

        if not users:
            return

        # Fetch all lessons for today matching current week
        lessons_query = (
            select(Lesson)
            .where(
                Lesson.weekday == weekday,
                Lesson.week_type.in_(["EVERY", current_week_type])
            )
            .options(
                selectinload(Lesson.subject),
                selectinload(Lesson.teacher),
                selectinload(Lesson.room),
                selectinload(Lesson.group)
            )
        )
        lessons_res = await session.execute(lessons_query)
        today_lessons = list(lessons_res.scalars().all())

        # Map lessons by group_id
        group_lessons_map = {}
        for l in today_lessons:
            group_lessons_map.setdefault(l.group_id, []).append(l)

        # Iterate over users
        for user in users:
            lessons_for_group = group_lessons_map.get(user.selected_group_id, [])
            for lesson in lessons_for_group:
                # Calculate lesson start datetime
                try:
                    start_hour, start_min = map(int, lesson.start_time.split(":"))
                    lesson_start_dt = datetime.combine(today_date, datetime.min.time()).replace(
                        hour=start_hour, minute=start_min
                    )
                except Exception:
                    continue

                lead_minutes = user.reminder_lead_minutes or settings.DEFAULT_REMINDER_LEAD_MINUTES
                time_diff = (lesson_start_dt - now).total_seconds() / 60.0

                # Check if lesson starts in (lead_minutes - 2) to (lead_minutes + 1) minutes
                if 0 <= time_diff <= (lead_minutes + 1.5):
                    # Check if already sent
                    chk = await session.execute(
                        select(SentReminder).where(
                            SentReminder.user_id == user.id,
                            SentReminder.lesson_id == lesson.id,
                            SentReminder.reminder_date == today_str
                        )
                    )
                    if chk.scalars().first():
                        continue

                    # Send reminder
                    teacher_name = lesson.teacher.full_name if lesson.teacher else "Belgilanmagan"
                    room_code = lesson.room.code if lesson.room else "Noma'lum"
                    l_type = t("lesson_types").get(lesson.lesson_type, lesson.lesson_type)

                    msg_text = t(
                        "reminder_alert",
                        minutes=int(round(time_diff)),
                        subject=lesson.subject.name,
                        lesson_type=l_type,
                        start_time=lesson.start_time,
                        end_time=lesson.end_time,
                        room=room_code,
                        teacher=teacher_name,
                        group_name=lesson.group.name
                    )

                    try:
                        await bot.send_message(
                            chat_id=user.id,
                            text=msg_text,
                            parse_mode="HTML"
                        )
                        # Mark as sent
                        session.add(
                            SentReminder(
                                user_id=user.id,
                                lesson_id=lesson.id,
                                reminder_date=today_str
                            )
                        )
                        await session.commit()
                        logger.info(f"Reminder sent to user {user.id} for lesson {lesson.id}")
                    except TelegramRetryAfter as e:
                        logger.warning(f"Flood limit reached. Sleeping for {e.retry_after}s")
                        await asyncio.sleep(e.retry_after)
                    except TelegramForbiddenError:
                        logger.info(f"User {user.id} blocked bot. Marking inactive.")
                        user.is_active = False
                        await session.commit()
                    except TelegramAPIError as e:
                        logger.error(f"Error sending reminder to {user.id}: {e}")

                    # Rate limiting: 25 msgs/sec max (sleep ~0.04s)
                    await asyncio.sleep(0.04)
