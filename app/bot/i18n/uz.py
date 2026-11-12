"""Uzbek (Latin) localization strings for TSUE Telegram Bot."""

I18N = {
    # Greetings & Start
    "welcome": (
        "Assalomu alaykum, <b>{full_name}</b>!\n\n"
        "🏛 <b>Toshkent Davlat Iqtisodiyot Universiteti (TDIU)</b> dars jadvali botiga xush kelibsiz.\n\n"
        "Ushbu bot orqali siz:\n"
        "• Dars jadvalini qulay ko'rinishda (matn va rasm formatida) olishingiz\n"
        "• Darsdan 10 daqiqa oldin avtomatik eslatmalar qabul qilishingiz\n"
        "• Juft/toq hafta (A/B) jadvallarini ko'rishingiz\n"
        "• Botni o'z guruhingiz Telegram guruhiga qo'shib, har kuni ertalab avtomatik jadval olishingiz mumkin.\n\n"
        "Iltimos, pastdagi tugmalar orqali o'z guruhingizni tanlang:"
    ),
    "choose_group": "Iltimos, o'z guruhingizni tanlang yoki qidirish uchun guruh nomini yozing (masalan: <code>MMT-950/26i</code>):",
    "group_selected": "✅ Guruhingiz muvaffaqiyatli tanlandi: <b>{group_name}</b>!\n\nEndi quyidagi menyu orqali dars jadvalingizni ko'rishingiz mumkin:",
    "current_group": "Sizning guruhingiz: <b>{group_name}</b>",
    "no_group_selected": "⚠️ Siz hali guruh tanlamagansiz. Iltimos, avval guruhingizni tanlang:",
    
    # Menu buttons
    "btn_today": "📅 Bugungi darslar",
    "btn_tomorrow": "🗓 Ertangi darslar",
    "btn_this_week": "📆 Bu haftalik jadval",
    "btn_next_week": "⏭ Keyingi hafta jadvali",
    "btn_change_group": "🔄 Guruhni o'zgartirish",
    "btn_settings": "⚙️ Sozlamalar",
    "btn_help": "ℹ️ Yordam",
    
    # Timetable views
    "today_title": "📅 <b>{day_name} ({date_str}) — Bugungi darslar</b>\nGuruh: <b>{group_name}</b> (Hafta: <b>{week_type}</b>)\n",
    "tomorrow_title": "🗓 <b>{day_name} ({date_str}) — Ertangi darslar</b>\nGuruh: <b>{group_name}</b> (Hafta: <b>{week_type}</b>)\n",
    "week_title": "📆 <b>{group_name} guruhining haftalik dars jadvali</b>\nDavr: {date_range} | Hafta: <b>{week_type}</b>",
    "no_lessons_today": "🎉 Bugun hech qanday dars yo'q! Maroqli dam oling.",
    "no_lessons_tomorrow": "🎉 Ertaga darslar yo'q! Dam olishingiz mumkin.",
    "free_day": "Dam olish kuni",
    
    # Lesson formatting
    "lesson_item": (
        "\n<b>{slot}-para | {start_time} - {end_time}</b>\n"
        "📚 <b>{subject}</b> ({lesson_type})\n"
        "👨‍🏫 O'qituvchi: {teacher}\n"
        "📍 Xona: <code>{room}</code>\n"
    ),
    
    # Settings
    "settings_title": (
        "⚙️ <b>Sozlamalar menyusi</b>\n\n"
        "• Hozirgi guruh: <b>{group_name}</b>\n"
        "• Eslatmalar: <b>{reminders_status}</b>\n"
        "• Eslatma vaqti: <b>{lead_minutes} daqiqa oldin</b>\n"
    ),
    "reminders_enabled": "Yoqilgan ✅",
    "reminders_disabled": "O'chirilgan ❌",
    "btn_toggle_reminders": "🔔 Eslatmalarni o'zgartirish",
    "btn_lead_time": "⏱ Eslatma vaqtini sozlash",
    "choose_lead_time": "Dars boshlanishidan necha daqiqa oldin eslatma yuborilsin?",
    "lead_time_updated": "✅ Eslatma vaqti <b>{minutes} daqiqa</b> qilib belgilandi.",
    "reminders_toggled": "✅ Eslatmalar holati o'zgartirildi: <b>{status}</b>",
    
    # Reminder text
    "reminder_alert": (
        "⏰ <b>Dars boshlanishiga {minutes} daqiqa qoldi!</b>\n\n"
        "📚 Fan: <b>{subject}</b> ({lesson_type})\n"
        "⏰ Vaqt: <b>{start_time} - {end_time}</b>\n"
        "📍 Xona: <code>{room}</code>\n"
        "👨‍🏫 O'qituvchi: <b>{teacher}</b>\n"
        "🏛 Guruh: <b>{group_name}</b>"
    ),
    
    # Group chats
    "group_chat_help": (
        "👥 <b>Guruh chatida botdan foydalanish:</b>\n\n"
        "1. Botni guruhingizga admin qilib qo'shing\n"
        "2. Guruhga biriktirish: <code>/setgroup MMT-950/26i</code>\n"
        "3. Kunlik jadval yuborish vaqtini o'rnatish: <code>/settime 07:00</code>\n"
        "4. Jadvalni to'xtatish: <code>/stop</code>\n"
    ),
    "group_linked_success": "✅ Ushbu guruh muvaffaqiyatli <b>{group_name}</b> guruhiga biriktirildi!\nHar kuni soat <b>{time}</b> da kunlik jadval yuborib turiladi.",
    "group_not_admin": "⚠️ Ushbu buyruqni faqat guruh adminlari bajara oladi.",
    "group_unlinked": "✅ Guruhga avtomatik jadval yuborish to'xtatildi.",
    "group_invalid_format": "⚠️ Noto'g'ri format. Misol: <code>/setgroup MMT-950/26i</code>",
    "time_invalid_format": "⚠️ Noto'g'ri vaqt formati. Misol: <code>/settime 07:00</code> (00:00 dan 23:59 gacha)",
    
    # Admin commands & alerts
    "admin_welcome": "🔐 <b>Admin paneliga xush kelibsiz!</b>\nQuyidagi amallardan birini tanlang:",
    "admin_stats": (
        "📊 <b>Bot statistikasi:</b>\n\n"
        "👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        "🟢 Faol foydalanuvchilar: <b>{active_users}</b>\n"
        "👥 Biriktirilgan guruh chatlari: <b>{total_chats}</b>\n"
        "🏛 Mavjud guruhlar soni: <b>{total_groups}</b>\n"
        "📚 Jami darslar soni: <b>{total_lessons}</b>\n"
        "📩 Bugun yuborilgan eslatmalar: <b>{today_reminders}</b>"
    ),
    "admin_broadcast_prompt": (
        "📢 <b>Xabar tarqatish (Broadcast)</b>\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabarni kiriting (matn, rasm yoki formatlangan xabar):"
    ),
    "admin_broadcast_confirm": (
        "⚠️ <b>Tasdiqlash kodi:</b>\n\n"
        "Xabarni <b>{count}</b> ta foydalanuvchiga yuborishni tasdiqlash uchun quyidagi 4 xonali kodni yozing:\n"
        "🔑 Tasdiq kodi: <code>{code}</code>\n\n"
        "Bekor qilish uchun <code>/cancel</code> yozing."
    ),
    "admin_broadcast_started": "🚀 Xabar tarqatish boshlandi...",
    "admin_broadcast_finished": (
        "✅ <b>Xabar tarqatish yakunlandi:</b>\n\n"
        "• Yuborildi: <b>{sent}</b> ta\n"
        "• Bloklangan/Xatolik: <b>{failed}</b> ta"
    ),
    "admin_backup_success": "💾 Ma'lumotlar bazasi nusxasi (backup) muvaffaqiyatli yaratildi va siqildi.",
    "admin_sync_success": "🔄 Dars jadvallari muvaffaqiyatli sinxronizatsiya qilindi va keshlar yangilandi.",
    "access_denied": "⛔️ Kechirasiz, sizda ushbu buyruqdan foydalanish huquqi yo'q.",
    "unknown_command": "Kechirasiz, buyruq tushunarsiz. /help orqali ma'lumot olishingiz mumkin.",
    
    # Week days in Uzbek
    "weekdays": {
        1: "Dushanba",
        2: "Seshanba",
        3: "Chorshanba",
        4: "Payshanba",
        5: "Juma",
        6: "Shanba",
        7: "Yakshanba"
    },
    
    # Lesson types in Uzbek
    "lesson_types": {
        "Ma": "Ma'ruza",
        "Sem": "Amaliy/Seminar",
        "Lab": "Laboratoriya",
        "Sport": "Jismoniy tarbiya",
        "Boshqa": "Mashg'ulot"
    }
}


def t(key: str, **kwargs) -> str:
    """Helper to get translated string with formatting."""
    text = I18N.get(key, key)
    if isinstance(text, str) and kwargs:
        return text.format(**kwargs)
    return text
