from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from sqlalchemy import select

from app.core.models import User, Group
from app.core.db import AsyncSessionLocal
from app.bot.i18n.uz import t
from app.bot.keyboards.default import get_main_menu_keyboard
from app.bot.keyboards.inline import get_group_selection_keyboard
from app.services.timetable import get_all_groups, get_group_by_name

router = Router(name="common_router")


async def get_or_create_user(message: Message) -> User:
    """Ensure user exists in DB and update their profile info."""
    from_user = message.from_user
    async with AsyncSessionLocal() as session:
        user = await session.get(User, from_user.id)
        if not user:
            user = User(
                id=from_user.id,
                username=from_user.username,
                full_name=from_user.full_name or "Talaba",
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            # Update user info if changed
            if user.username != from_user.username or user.full_name != from_user.full_name or not user.is_active:
                user.username = from_user.username
                user.full_name = from_user.full_name or user.full_name
                user.is_active = True
                await session.commit()
        return user


@router.message(CommandStart())
async def handle_start(message: Message):
    # Only in private chat
    if message.chat.type != "private":
        await message.answer(t("group_chat_help"), parse_mode="HTML")
        return

    user = await get_or_create_user(message)
    groups = await get_all_groups()

    if not user.selected_group_id:
        welcome_text = t("welcome", full_name=message.from_user.full_name or "Talaba")
        kb = get_group_selection_keyboard(groups, page=0)
        await message.answer(welcome_text, reply_markup=kb, parse_mode="HTML")
    else:
        async with AsyncSessionLocal() as session:
            selected_grp = await session.get(Group, user.selected_group_id)
            group_name = selected_grp.name if selected_grp else "MMT-950/26i"

        text = (
            f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
            f"{t('current_group', group_name=group_name)}\n"
            f"Dars jadvalini ko'rish uchun quyidagi tugmalardan foydalaning:"
        )
        await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")


@router.message(Command("help"))
@router.message(F.text == t("btn_help"))
async def handle_help(message: Message):
    help_text = (
        "ℹ️ <b>TSUE Dars Jadvali Boti haqida:</b>\n\n"
        "• <b>Bugungi darslar</b> — bugungi kun bo'yicha to'liq ma'lumot (fan, xona, o'qituvchi).\n"
        "• <b>Ertangi darslar</b> — ertangi kun darslari.\n"
        "• <b>Haftalik jadval</b> — aSc Timetables uslubidagi rangli rasmli jadval.\n"
        "• <b>Eslatmalar</b> — dars boshlanishidan 10 daqiqa oldin xabar yuboriladi.\n"
        "• <b>Guruh chatlariga qo'shish</b> — botni guruhingizga qo'shib <code>/setgroup Guruh_Nomi</code> buyrug'ini yuboring.\n\n"
        "📞 Savol yoki takliflar bo'lsa universitet mas'ullariga murojaat qilishingiz mumkin."
    )
    await message.answer(help_text, parse_mode="HTML")


@router.message(F.text == t("btn_change_group"))
async def handle_change_group(message: Message):
    groups = await get_all_groups()
    kb = get_group_selection_keyboard(groups, page=0)
    await message.answer(t("choose_group"), reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("grp_page:"))
async def handle_group_pagination(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    groups = await get_all_groups()
    kb = get_group_selection_keyboard(groups, page=page)
    await callback.message.edit_reply_markup(reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("sel_grp:"))
async def handle_group_selection(callback: CallbackQuery):
    group_id = int(callback.data.split(":")[1])
    async with AsyncSessionLocal() as session:
        group = await session.get(Group, group_id)
        if not group:
            await callback.answer("Guruh topilmadi!", show_alert=True)
            return

        user = await session.get(User, callback.from_user.id)
        if not user:
            user = User(
                id=callback.from_user.id,
                username=callback.from_user.username,
                full_name=callback.from_user.full_name or "Talaba",
                selected_group_id=group.id,
                is_active=True
            )
            session.add(user)
        else:
            user.selected_group_id = group.id
        await session.commit()

    await callback.answer(f"✅ {group.name} tanlandi!")
    await callback.message.delete()
    await callback.message.answer(
        t("group_selected", group_name=group.name),
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "reselect_group")
async def handle_reselect_group(callback: CallbackQuery):
    groups = await get_all_groups()
    kb = get_group_selection_keyboard(groups, page=0)
    await callback.message.answer(t("choose_group"), reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.message(F.text.regexp(r"^[A-Za-z0-9\-\/_]+$"))
async def handle_group_search(message: Message):
    """Allow typing group name directly (e.g. 'MMT-950/26i' or '950')."""
    if message.chat.type != "private":
        return

    text = message.text.strip()
    if text.startswith("/"):
        return

    async with AsyncSessionLocal() as session:
        query = select(Group).where(Group.name.ilike(f"%{text}%"))
        res = await session.execute(query)
        matching_groups = list(res.scalars().all())

    if not matching_groups:
        return

    if len(matching_groups) == 1:
        group = matching_groups[0]
        async with AsyncSessionLocal() as session:
            user = await session.get(User, message.from_user.id)
            if user:
                user.selected_group_id = group.id
                await session.commit()
        await message.answer(
            t("group_selected", group_name=group.name),
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
    else:
        kb = get_group_selection_keyboard(matching_groups, page=0)
        await message.answer(
            f"🔍 <b>\"{text}\"</b> bo'yicha topilgan guruhlar:",
            reply_markup=kb,
            parse_mode="HTML"
        )
