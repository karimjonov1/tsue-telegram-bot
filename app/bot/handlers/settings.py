from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from app.core.models import User, Group
from app.core.db import AsyncSessionLocal
from app.bot.i18n.uz import t
from app.bot.keyboards.inline import get_settings_keyboard, get_lead_time_keyboard

router = Router(name="settings_router")


@router.message(F.text == t("btn_settings"))
async def handle_settings(message: Message):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            return
        
        group_name = "Tanlanmagan"
        if user.selected_group_id:
            grp = await session.get(Group, user.selected_group_id)
            if grp:
                group_name = grp.name

        status = t("reminders_enabled") if user.reminders_enabled else t("reminders_disabled")
        text = t(
            "settings_title",
            group_name=group_name,
            reminders_status=status,
            lead_minutes=user.reminder_lead_minutes
        )
        kb = get_settings_keyboard(user.reminders_enabled)
        await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "toggle_reminders")
async def handle_toggle_reminders(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer()
            return
        
        user.reminders_enabled = not user.reminders_enabled
        await session.commit()
        new_state = user.reminders_enabled
        new_lead = user.reminder_lead_minutes
        group_id = user.selected_group_id

    status_str = t("reminders_enabled") if new_state else t("reminders_disabled")
    await callback.answer(f"Eslatmalar: {status_str}")

    group_name = "Tanlanmagan"
    if group_id:
        async with AsyncSessionLocal() as session:
            grp = await session.get(Group, group_id)
            if grp:
                group_name = grp.name

    new_text = t(
        "settings_title",
        group_name=group_name,
        reminders_status=status_str,
        lead_minutes=new_lead
    )
    await callback.message.edit_text(new_text, reply_markup=get_settings_keyboard(new_state), parse_mode="HTML")


@router.callback_query(F.data == "set_lead_time")
async def handle_set_lead_time(callback: CallbackQuery):
    await callback.message.edit_text(
        t("choose_lead_time"),
        reply_markup=get_lead_time_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lead:"))
async def handle_save_lead_time(callback: CallbackQuery):
    minutes = int(callback.data.split(":")[1])
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if user:
            user.reminder_lead_minutes = minutes
            await session.commit()
            reminders_enabled = user.reminders_enabled
            group_id = user.selected_group_id

    await callback.answer(f"✅ {minutes} daqiqa saqlandi!")

    group_name = "Tanlanmagan"
    if group_id:
        async with AsyncSessionLocal() as session:
            grp = await session.get(Group, group_id)
            if grp:
                group_name = grp.name

    status_str = t("reminders_enabled") if reminders_enabled else t("reminders_disabled")
    text = t(
        "settings_title",
        group_name=group_name,
        reminders_status=status_str,
        lead_minutes=minutes
    )
    await callback.message.edit_text(text, reply_markup=get_settings_keyboard(reminders_enabled), parse_mode="HTML")


@router.callback_query(F.data == "settings_back")
async def handle_settings_back(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer()
            return
        
        group_name = "Tanlanmagan"
        if user.selected_group_id:
            grp = await session.get(Group, user.selected_group_id)
            if grp:
                group_name = grp.name

        status = t("reminders_enabled") if user.reminders_enabled else t("reminders_disabled")
        text = t(
            "settings_title",
            group_name=group_name,
            reminders_status=status,
            lead_minutes=user.reminder_lead_minutes
        )
        kb = get_settings_keyboard(user.reminders_enabled)
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
