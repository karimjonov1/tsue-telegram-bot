from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.core.models import Group


def get_group_selection_keyboard(groups: List[Group], page: int = 0, per_page: int = 6) -> InlineKeyboardMarkup:
    """Inline keyboard for selecting student groups with pagination."""
    total_groups = len(groups)
    start_idx = page * per_page
    end_idx = start_idx + per_page
    current_page_groups = groups[start_idx:end_idx]

    kb = []
    # Two buttons per row
    row = []
    for g in current_page_groups:
        row.append(InlineKeyboardButton(text=f"🏛 {g.name}", callback_data=f"sel_grp:{g.id}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)

    # Navigation buttons
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Ortga", callback_data=f"grp_page:{page - 1}"))
    if end_idx < total_groups:
        nav_row.append(InlineKeyboardButton(text="Oldinga ▶️", callback_data=f"grp_page:{page + 1}"))
    
    if nav_row:
        kb.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_settings_keyboard(reminders_enabled: bool) -> InlineKeyboardMarkup:
    """Settings inline keyboard."""
    status_icon = "❌ O'chirish" if reminders_enabled else "✅ Yoqish"
    kb = [
        [
            InlineKeyboardButton(text=f"🔔 Eslatmalarni {status_icon}", callback_data="toggle_reminders")
        ],
        [
            InlineKeyboardButton(text="⏱ Eslatma vaqtini sozlash", callback_data="set_lead_time")
        ],
        [
            InlineKeyboardButton(text="🔄 Boshqa guruhni tanlash", callback_data="reselect_group")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_lead_time_keyboard() -> InlineKeyboardMarkup:
    """Select lead time for reminders."""
    kb = [
        [
            InlineKeyboardButton(text="5 daqiqa oldin", callback_data="lead:5"),
            InlineKeyboardButton(text="10 daqiqa oldin", callback_data="lead:10"),
        ],
        [
            InlineKeyboardButton(text="15 daqiqa oldin", callback_data="lead:15"),
            InlineKeyboardButton(text="30 daqiqa oldin", callback_data="lead:30"),
        ],
        [
            InlineKeyboardButton(text="◀️ Ortga", callback_data="settings_back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
