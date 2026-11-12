from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.core.models import Group, Lesson, Subject, Teacher, Room
from app.core.db import AsyncSessionLocal
from app.bot.i18n.uz import t


def get_semester_start_date() -> date:
    """Parse configured semester start date."""
    try:
        return datetime.strptime(settings.SEMESTER_START_DATE, "%Y-%m-%d").date()
    except Exception:
        return date(2026, 9, 7)


def get_week_info(target_date: Optional[date] = None) -> Tuple[str, int]:
    """
    Calculate whether a given date is in Week A (Toq) or Week B (Juft),
    along with the 1-based semester week number.
    """
    if target_date is None:
        target_date = date.today()
    
    start_date = get_semester_start_date()
    delta_days = (target_date - start_date).days
    
    # If before semester start, default to Week 1 (Week A)
    if delta_days < 0:
        week_number = 1
    else:
        week_number = (delta_days // 7) + 1

    week_type = "WEEK_A" if (week_number % 2 != 0) else "WEEK_B"
    return week_type, week_number


def get_week_type_display(week_type: str) -> str:
    if week_type == "WEEK_A":
        return "A-hafta (Toq)"
    elif week_type == "WEEK_B":
        return "B-hafta (Juft)"
    return "Har hafta"


async def get_group_by_name(group_name: str) -> Optional[Group]:
    async with AsyncSessionLocal() as session:
        query = select(Group).where(Group.name.ilike(group_name.strip()))
        result = await session.execute(query)
        return result.scalars().first()


async def get_all_groups() -> List[Group]:
    async with AsyncSessionLocal() as session:
        query = select(Group).where(Group.is_active == True).order_by(Group.name)
        result = await session.execute(query)
        return list(result.scalars().all())


async def get_lessons_for_day(
    group_id: int,
    target_date: date
) -> Tuple[List[Lesson], str]:
    """
    Fetch lessons for a group on a specific date, filtering by Week A / Week B.
    Weekday: 1=Monday .. 7=Sunday
    """
    weekday = target_date.isoweekday()  # 1 to 7
    if weekday > 6:
        # Sunday - no university classes
        return [], "WEEK_A"

    current_week_type, _ = get_week_info(target_date)

    async with AsyncSessionLocal() as session:
        query = (
            select(Lesson)
            .where(
                Lesson.group_id == group_id,
                Lesson.weekday == weekday,
                Lesson.week_type.in_(["EVERY", current_week_type])
            )
            .options(
                selectinload(Lesson.subject),
                selectinload(Lesson.teacher),
                selectinload(Lesson.room),
                selectinload(Lesson.group)
            )
            .order_by(Lesson.slot_number)
        )
        result = await session.execute(query)
        lessons = list(result.scalars().all())
        return lessons, current_week_type


async def get_lessons_for_full_week(
    group_id: int,
    target_date: date
) -> Tuple[Dict[int, List[Lesson]], str, date, date]:
    """
    Fetch all lessons for the Monday-Saturday week of the given target_date.
    Returns: (dict[weekday, list[Lesson]], week_type, monday_date, saturday_date)
    """
    # Find Monday of this week
    monday = target_date - timedelta(days=target_date.weekday())
    saturday = monday + timedelta(days=5)
    current_week_type, _ = get_week_info(monday)

    async with AsyncSessionLocal() as session:
        query = (
            select(Lesson)
            .where(
                Lesson.group_id == group_id,
                Lesson.week_type.in_(["EVERY", current_week_type])
            )
            .options(
                selectinload(Lesson.subject),
                selectinload(Lesson.teacher),
                selectinload(Lesson.room),
                selectinload(Lesson.group)
            )
            .order_by(Lesson.weekday, Lesson.slot_number)
        )
        result = await session.execute(query)
        lessons = list(result.scalars().all())

    by_weekday: Dict[int, List[Lesson]] = {i: [] for i in range(1, 7)}
    for l in lessons:
        by_weekday[l.weekday].append(l)

    return by_weekday, current_week_type, monday, saturday


def format_day_schedule_text(
    group_name: str,
    target_date: date,
    lessons: List[Lesson],
    week_type: str,
    is_tomorrow: bool = False
) -> str:
    """Format single day schedule into natural Uzbek markdown text."""
    weekday = target_date.isoweekday()
    day_name = t("weekdays").get(weekday, "Noma'lum kun")
    date_str = target_date.strftime("%d.%m.%Y")
    week_str = get_week_type_display(week_type)

    if is_tomorrow:
        header = t("tomorrow_title", day_name=day_name, date_str=date_str, group_name=group_name, week_type=week_str)
    else:
        header = t("today_title", day_name=day_name, date_str=date_str, group_name=group_name, week_type=week_str)

    if not lessons:
        empty_msg = t("no_lessons_tomorrow") if is_tomorrow else t("no_lessons_today")
        return f"{header}\n{empty_msg}"

    body = header
    for lesson in lessons:
        l_type = t("lesson_types").get(lesson.lesson_type, lesson.lesson_type)
        teacher_name = lesson.teacher.full_name if lesson.teacher else "Belgilanmagan"
        room_code = lesson.room.code if lesson.room else "Noma'lum"
        body += t(
            "lesson_item",
            slot=lesson.slot_number,
            start_time=lesson.start_time,
            end_time=lesson.end_time,
            subject=lesson.subject.name,
            lesson_type=l_type,
            teacher=teacher_name,
            room=room_code
        )

    return body
