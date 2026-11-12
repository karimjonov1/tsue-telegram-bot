from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.bot.i18n.uz import t


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard for TSUE students."""
    kb = [
        [
            KeyboardButton(text=t("btn_today")),
            KeyboardButton(text=t("btn_tomorrow")),
        ],
        [
            KeyboardButton(text=t("btn_this_week")),
            KeyboardButton(text=t("btn_next_week")),
        ],
        [
            KeyboardButton(text=t("btn_change_group")),
            KeyboardButton(text=t("btn_settings")),
        ],
        [
            KeyboardButton(text=t("btn_help")),
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Kerakli bo'limni tanlang..."
    )
