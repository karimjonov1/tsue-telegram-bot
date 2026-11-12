import json
import glob
import os
from typing import Dict, Any, List, Tuple, Optional
from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.models import Group, Lesson, Subject, Teacher, Room, ChangeLog, User, ChatLink
from app.core.db import AsyncSessionLocal
from app.core.logging import logger
from app.providers.base import TimetableProvider, LessonDTO
from app.bot.i18n.uz import t


async def diff_and_sync_timetable(
    provider: TimetableProvider,
    bot: Optional[Bot] = None
) -> Dict[str, Any]:
    """
    Sync timetable from provider, diff against DB, notify affected groups,
    and invalidate rendered image cache.
    """
    groups = await provider.fetch_groups()
    new_lessons = await provider.fetch_lessons()
    
    # Map new lessons by (group_name, weekday, slot_number, week_type)
    new_map: Dict[Tuple[str, int, int, str], LessonDTO] = {
        (l.group_name.upper(), l.weekday, l.slot_number, l.week_type): l
        for l in new_lessons
    }

    changes_by_group: Dict[str, List[str]] = {}

    async with AsyncSessionLocal() as session:
        # Fetch all existing lessons
        query = (
            select(Lesson)
            .options(
                selectinload(Lesson.group),
                selectinload(Lesson.subject),
                selectinload(Lesson.teacher),
                selectinload(Lesson.room)
            )
        )
        res = await session.execute(query)
        existing_lessons = list(res.scalars().all())

        existing_map: Dict[Tuple[str, int, int, str], Lesson] = {
            (l.group.name.upper(), l.weekday, l.slot_number, l.week_type): l
            for l in existing_lessons
        }

        # Check for additions and modifications
        for key, new_l in new_map.items():
            g_name, wday, slot, wtype = key
            if key not in existing_map:
                # ADDED
                msg = f"➕ Qo'shildi: {wday}-kun, {slot}-para: {new_l.subject_name} ({new_l.lesson_type}) - {new_l.room_code or ''}"
                changes_by_group.setdefault(g_name, []).append(msg)
            else:
                curr = existing_map[key]
                # Check if subject, teacher or room changed
                curr_teacher = curr.teacher.full_name if curr.teacher else None
                curr_room = curr.room.code if curr.room else None
                if (
                    curr.subject.name != new_l.subject_name or
                    curr_teacher != new_l.teacher_name or
                    curr_room != new_l.room_code or
                    curr.lesson_type != new_l.lesson_type
                ):
                    msg = (
                        f"✏️ O'zgardi: {wday}-kun, {slot}-para: {new_l.subject_name} "
                        f"({curr_room or ''} ➔ {new_l.room_code or ''})"
                    )
                    changes_by_group.setdefault(g_name, []).append(msg)

        # Check for removals
        for key, curr in existing_map.items():
            if key not in new_map:
                g_name, wday, slot, wtype = key
                msg = f"❌ O'chirildi: {wday}-kun, {slot}-para: {curr.subject.name}"
                changes_by_group.setdefault(g_name, []).append(msg)

        # Record changes in database and invalidate cache
        for g_name, diff_items in changes_by_group.items():
            g_res = await session.execute(select(Group).where(Group.name.ilike(g_name)))
            group_obj = g_res.scalars().first()
            if group_obj:
                ch = ChangeLog(
                    group_id=group_obj.id,
                    change_type="MODIFIED",
                    details=json.dumps(diff_items, ensure_ascii=False)
                )
                session.add(ch)

            # Invalidate image cache for this group
            safe_g_name = g_name.replace("/", "_").replace("\\", "_")
            pattern = os.path.join(settings.CACHE_DIR, f"{safe_g_name}_*.png")
            for f in glob.glob(pattern):
                try:
                    os.remove(f)
                    logger.info(f"Invalidated cache file: {f}")
                except Exception as e:
                    logger.error(f"Error removing cache file {f}: {e}")

        await session.commit()

    # If bot is passed and there are changes, alert affected users/groups
    if bot and changes_by_group:
        async with AsyncSessionLocal() as session:
            for g_name, diff_list in changes_by_group.items():
                g_res = await session.execute(select(Group).where(Group.name.ilike(g_name)))
                group_obj = g_res.scalars().first()
                if not group_obj:
                    continue

                diff_text = "\n".join(diff_list)
                alert_text = (
                    f"📢 <b>Diqqat, {group_obj.name} guruhida dars jadvali o'zgardi!</b>\n\n"
                    f"{diff_text}\n\n"
                    f"Yangilangan dars jadvalini ko'rish uchun menyudagi tugmalardan foydalaning."
                )

                # Send to subscribed users
                u_res = await session.execute(
                    select(User).where(User.selected_group_id == group_obj.id, User.is_active == True)
                )
                users = list(u_res.scalars().all())
                for u in users:
                    try:
                        await bot.send_message(chat_id=u.id, text=alert_text, parse_mode="HTML")
                    except Exception:
                        pass

                # Send to linked group chats
                c_res = await session.execute(
                    select(ChatLink).where(ChatLink.group_id == group_obj.id, ChatLink.is_active == True)
                )
                chats = list(c_res.scalars().all())
                for c in chats:
                    try:
                        await bot.send_message(chat_id=c.chat_id, text=alert_text, parse_mode="HTML")
                    except Exception:
                        pass

    return {
        "groups_checked": len(groups),
        "total_lessons_checked": len(new_lessons),
        "changes_detected": changes_by_group
    }
