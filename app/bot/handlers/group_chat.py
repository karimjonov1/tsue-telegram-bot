import re
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select

from app.core.models import Group, ChatLink
from app.core.db import AsyncSessionLocal
from app.bot.i18n.uz import t
from app.services.timetable import get_group_by_name

router = Router(name="group_chat_router")


async def is_chat_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    """Check if the user is administrator or owner of the chat."""
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in ["creator", "administrator"]
    except Exception:
        return False


@router.message(Command("setgroup"))
async def handle_set_group(message: Message, bot: Bot):
    if message.chat.type == "private":
        await message.answer("⚠️ Ushbu buyruq faqat guruh chatlarida ishlaydi.")
        return

    # Check admin rights
    if not await is_chat_admin(bot, message.chat.id, message.from_user.id):
        await message.answer(t("group_not_admin"))
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(t("group_invalid_format"), parse_mode="HTML")
        return

    group_input = parts[1].strip()
    group = await get_group_by_name(group_input)
    if not group:
        await message.answer(
            f"⚠️ <b>{group_input}</b> nomli guruh topilmadi. Masalan: <code>MMT-950/26i</code>",
            parse_mode="HTML"
        )
        return

    async with AsyncSessionLocal() as session:
        chat_link = await session.get(ChatLink, message.chat.id)
        if not chat_link:
            chat_link = ChatLink(
                chat_id=message.chat.id,
                title=message.chat.title or "Guruh",
                group_id=group.id,
                auto_post_time="07:00",
                is_active=True,
                linked_by=message.from_user.id
            )
            session.add(chat_link)
        else:
            chat_link.group_id = group.id
            chat_link.title = message.chat.title or chat_link.title
            chat_link.is_active = True
            chat_link.linked_by = message.from_user.id
        await session.commit()

    await message.answer(
        t("group_linked_success", group_name=group.name, time=chat_link.auto_post_time),
        parse_mode="HTML"
    )


@router.message(Command("settime"))
async def handle_set_time(message: Message, bot: Bot):
    if message.chat.type == "private":
        await message.answer("⚠️ Ushbu buyruq faqat guruh chatlarida ishlaydi.")
        return

    if not await is_chat_admin(bot, message.chat.id, message.from_user.id):
        await message.answer(t("group_not_admin"))
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(t("time_invalid_format"), parse_mode="HTML")
        return

    time_str = parts[1].strip()
    if not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", time_str):
        await message.answer(t("time_invalid_format"), parse_mode="HTML")
        return

    # Normalize HH:MM
    if len(time_str.split(":")[0]) == 1:
        time_str = f"0{time_str}"

    async with AsyncSessionLocal() as session:
        chat_link = await session.get(ChatLink, message.chat.id)
        if not chat_link or not chat_link.is_active:
            await message.answer("⚠️ Avval guruhni biriktiring: <code>/setgroup MMT-950/26i</code>", parse_mode="HTML")
            return

        chat_link.auto_post_time = time_str
        await session.commit()

    await message.answer(f"✅ Har kuni soat <b>{time_str}</b> da avtomatik dars jadvali yuboriladi.", parse_mode="HTML")


@router.message(Command("stop"))
async def handle_stop_group(message: Message, bot: Bot):
    if message.chat.type == "private":
        return

    if not await is_chat_admin(bot, message.chat.id, message.from_user.id):
        await message.answer(t("group_not_admin"))
        return

    async with AsyncSessionLocal() as session:
        chat_link = await session.get(ChatLink, message.chat.id)
        if chat_link:
            chat_link.is_active = False
            await session.commit()

    await message.answer(t("group_unlinked"))
