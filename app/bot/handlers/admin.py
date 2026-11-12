import random
from datetime import date
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func

from app.core.config import settings
from app.core.models import User, Group, Lesson, ChatLink, SentReminder
from app.core.db import AsyncSessionLocal
from app.bot.i18n.uz import t
from app.bot.keyboards.admin_kb import get_admin_menu_keyboard
from app.bot.states.admin_states import AdminBroadcastState
from app.services.backup import create_and_send_backup
from app.services.sync import diff_and_sync_timetable
from app.services.broadcast import broadcast_message
from app.providers.tsue_seeded import TSUEImageSeededProvider

router = Router(name="admin_router")


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


@router.message(Command("admin"))
async def handle_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(t("access_denied"))
        return

    await message.answer(
        t("admin_welcome"),
        reply_markup=get_admin_menu_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("stats"))
@router.callback_query(F.data == "admin_stats")
async def handle_stats(event: Message | CallbackQuery):
    user_id = event.from_user.id
    if not is_admin(user_id):
        if isinstance(event, CallbackQuery):
            await event.answer(t("access_denied"), show_alert=True)
        else:
            await event.answer(t("access_denied"))
        return

    today_str = date.today().strftime("%Y-%m-%d")
    async with AsyncSessionLocal() as session:
        total_users = (await session.execute(select(func.count(User.id)))).scalar() or 0
        active_users = (await session.execute(select(func.count(User.id)).where(User.is_active == True))).scalar() or 0
        total_chats = (await session.execute(select(func.count(ChatLink.chat_id)).where(ChatLink.is_active == True))).scalar() or 0
        total_groups = (await session.execute(select(func.count(Group.id)))).scalar() or 0
        total_lessons = (await session.execute(select(func.count(Lesson.id)))).scalar() or 0
        today_reminders = (await session.execute(
            select(func.count(SentReminder.id)).where(SentReminder.reminder_date == today_str)
        )).scalar() or 0

    stats_text = t(
        "admin_stats",
        total_users=total_users,
        active_users=active_users,
        total_chats=total_chats,
        total_groups=total_groups,
        total_lessons=total_lessons,
        today_reminders=today_reminders
    )

    if isinstance(event, CallbackQuery):
        await event.message.answer(stats_text, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(stats_text, parse_mode="HTML")


@router.message(Command("users"))
@router.callback_query(F.data == "admin_users")
async def handle_users(event: Message | CallbackQuery):
    user_id = event.from_user.id
    if not is_admin(user_id):
        return

    async with AsyncSessionLocal() as session:
        query = select(User).order_by(User.created_at.desc()).limit(15)
        res = await session.execute(query)
        recent_users = list(res.scalars().all())

    lines = ["👥 <b>So'nggi ro'yxatdan o'tgan foydalanuvchilar:</b>\n"]
    for u in recent_users:
        u_name = f"@{u.username}" if u.username else "username yo'q"
        status = "🟢" if u.is_active else "🔴"
        lines.append(f"{status} <b>{u.full_name}</b> ({u_name}) — <code>{u.id}</code>")

    reply_text = "\n".join(lines)
    if isinstance(event, CallbackQuery):
        await event.message.answer(reply_text, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(reply_text, parse_mode="HTML")


@router.message(Command("backup"))
@router.callback_query(F.data == "admin_backup")
async def handle_backup(event: Message | CallbackQuery, bot: Bot):
    user_id = event.from_user.id
    if not is_admin(user_id):
        return

    status_msg = None
    if isinstance(event, CallbackQuery):
        status_msg = await event.message.answer("⏳ Zaxira nusxa yaratilmoqda va siqilmoqda...")
        await event.answer()
    else:
        status_msg = await event.answer("⏳ Zaxira nusxa yaratilmoqda va siqilmoqda...")

    try:
        await create_and_send_backup(bot, user_id)
        if status_msg:
            await status_msg.delete()
    except Exception as e:
        if status_msg:
            await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")


@router.message(Command("sync"))
@router.callback_query(F.data == "admin_sync")
async def handle_sync(event: Message | CallbackQuery, bot: Bot):
    user_id = event.from_user.id
    if not is_admin(user_id):
        return

    status_msg = None
    if isinstance(event, CallbackQuery):
        status_msg = await event.message.answer("⏳ Dars jadvallari sinxronizatsiya qilinmoqda...")
        await event.answer()
    else:
        status_msg = await event.answer("⏳ Dars jadvallari sinxronizatsiya qilinmoqda...")

    provider = TSUEImageSeededProvider()
    result = await diff_and_sync_timetable(provider, bot=bot)

    summary = (
        f"✅ <b>Sinxronizatsiya yakunlandi:</b>\n\n"
        f"• Tekshirilgan guruhlar: <b>{result['groups_checked']}</b>\n"
        f"• Jami darslar: <b>{result['total_lessons_checked']}</b>\n"
        f"• Aniqlangan o'zgarishlar: <b>{len(result['changes_detected'])}</b> ta guruhda"
    )
    if status_msg:
        await status_msg.edit_text(summary, parse_mode="HTML")


# === 2-Step Broadcast Flow ===

@router.message(Command("broadcast"))
@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(event: Message | CallbackQuery, state: FSMContext):
    user_id = event.from_user.id
    if not is_admin(user_id):
        return

    await state.set_state(AdminBroadcastState.waiting_for_message)
    prompt = t("admin_broadcast_prompt")
    if isinstance(event, CallbackQuery):
        await event.message.answer(prompt, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(prompt, parse_mode="HTML")


@router.message(AdminBroadcastState.waiting_for_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Xabar tarqatish bekor qilindi.")
        return

    # Count target users
    async with AsyncSessionLocal() as session:
        active_count = (await session.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )).scalar() or 0

    # Generate 4-digit code
    confirm_code = f"{random.randint(1000, 9999)}"
    await state.update_data(
        broadcast_msg_id=message.message_id,
        broadcast_chat_id=message.chat.id,
        confirm_code=confirm_code
    )
    await state.set_state(AdminBroadcastState.waiting_for_confirm_code)

    await message.answer(
        t("admin_broadcast_confirm", count=active_count, code=confirm_code),
        parse_mode="HTML"
    )


@router.message(AdminBroadcastState.waiting_for_confirm_code)
async def confirm_broadcast(message: Message, state: FSMContext, bot: Bot):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Xabar tarqatish bekor qilindi.")
        return

    data = await state.get_data()
    expected_code = data.get("confirm_code")

    if message.text.strip() != expected_code:
        await message.answer("⚠️ Tasdiqlash kodi noto'g'ri. Qayta urinib ko'ring yoki /cancel yozing.")
        return

    # User confirmed!
    await message.answer(t("admin_broadcast_started"))
    source_chat_id = data["broadcast_chat_id"]
    source_msg_id = data["broadcast_msg_id"]

    # We use a dummy message reference to copy_to
    class MockMessage:
        async def copy_to(self, chat_id: int):
            return await bot.copy_message(
                chat_id=chat_id,
                from_chat_id=source_chat_id,
                message_id=source_msg_id
            )

    sent, failed = await broadcast_message(bot, MockMessage())  # type: ignore
    await state.clear()
    await message.answer(
        t("admin_broadcast_finished", sent=sent, failed=failed),
        parse_mode="HTML"
    )
