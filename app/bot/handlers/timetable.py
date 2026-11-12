from datetime import date, timedelta
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from sqlalchemy import select

from app.core.models import User, Group
from app.core.db import AsyncSessionLocal
from app.bot.i18n.uz import t
from app.services.timetable import (
    get_lessons_for_day,
    get_lessons_for_full_week,
    format_day_schedule_text,
    get_week_type_display
)
from app.services.renderer import render_timetable_image
from app.bot.keyboards.inline import get_group_selection_keyboard
from app.services.timetable import get_all_groups

router = Router(name="timetable_router")


async def get_user_group(message: Message) -> tuple[User, Group | None]:
    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user or not user.selected_group_id:
            return user, None
        group = await session.get(Group, user.selected_group_id)
        return user, group


@router.message(F.text == t("btn_today"))
async def handle_today(message: Message):
    user, group = await get_user_group(message)
    if not group:
        groups = await get_all_groups()
        await message.answer(
            t("no_group_selected"),
            reply_markup=get_group_selection_keyboard(groups, page=0),
            parse_mode="HTML"
        )
        return

    today = date.today()
    lessons, week_type = await get_lessons_for_day(group.id, today)
    text = format_day_schedule_text(
        group_name=group.name,
        target_date=today,
        lessons=lessons,
        week_type=week_type,
        is_tomorrow=False
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == t("btn_tomorrow"))
async def handle_tomorrow(message: Message):
    user, group = await get_user_group(message)
    if not group:
        groups = await get_all_groups()
        await message.answer(
            t("no_group_selected"),
            reply_markup=get_group_selection_keyboard(groups, page=0),
            parse_mode="HTML"
        )
        return

    tomorrow = date.today() + timedelta(days=1)
    lessons, week_type = await get_lessons_for_day(group.id, tomorrow)
    text = format_day_schedule_text(
        group_name=group.name,
        target_date=tomorrow,
        lessons=lessons,
        week_type=week_type,
        is_tomorrow=True
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == t("btn_this_week"))
async def handle_this_week(message: Message):
    user, group = await get_user_group(message)
    if not group:
        groups = await get_all_groups()
        await message.answer(
            t("no_group_selected"),
            reply_markup=get_group_selection_keyboard(groups, page=0),
            parse_mode="HTML"
        )
        return

    status_msg = await message.answer("⏳ Dars jadvali tasviri tayyorlanmoqda...")
    today = date.today()
    lessons_by_day, week_type, monday, saturday = await get_lessons_for_full_week(group.id, today)

    image_path = await render_timetable_image(group.name, lessons_by_day, week_type)

    date_range = f"{monday.strftime('%d.%m')} - {saturday.strftime('%d.%m.%Y')}"
    caption = t(
        "week_title",
        group_name=group.name,
        date_range=date_range,
        week_type=get_week_type_display(week_type)
    )

    photo = FSInputFile(image_path)
    await message.answer_photo(photo=photo, caption=caption, parse_mode="HTML")
    await status_msg.delete()


@router.message(F.text == t("btn_next_week"))
async def handle_next_week(message: Message):
    user, group = await get_user_group(message)
    if not group:
        groups = await get_all_groups()
        await message.answer(
            t("no_group_selected"),
            reply_markup=get_group_selection_keyboard(groups, page=0),
            parse_mode="HTML"
        )
        return

    status_msg = await message.answer("⏳ Keyingi hafta jadvali tayyorlanmoqda...")
    next_week_date = date.today() + timedelta(days=7)
    lessons_by_day, week_type, monday, saturday = await get_lessons_for_full_week(group.id, next_week_date)

    image_path = await render_timetable_image(group.name, lessons_by_day, week_type)

    date_range = f"{monday.strftime('%d.%m')} - {saturday.strftime('%d.%m.%Y')}"
    caption = (
        f"⏭ <b>{group.name} — Keyingi hafta dars jadvali</b>\n"
        f"Davr: {date_range} | Hafta: <b>{get_week_type_display(week_type)}</b>"
    )

    photo = FSInputFile(image_path)
    await message.answer_photo(photo=photo, caption=caption, parse_mode="HTML")
    await status_msg.delete()
