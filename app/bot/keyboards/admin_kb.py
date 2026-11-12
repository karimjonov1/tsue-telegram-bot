from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Admin panel main inline keyboard."""
    kb = [
        [
            InlineKeyboardButton(text="📊 Bot Statistikasi", callback_data="admin_stats"),
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
        ],
        [
            InlineKeyboardButton(text="📢 Xabar Tarqatish", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="🔄 Jadval Sinxronizatsiyasi", callback_data="admin_sync"),
        ],
        [
            InlineKeyboardButton(text="💾 SQLite Zaxira (Backup)", callback_data="admin_backup"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
