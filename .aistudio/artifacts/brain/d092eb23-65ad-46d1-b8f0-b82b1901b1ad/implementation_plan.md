# TSUE Dars Jadvali Telegram Boti — Arxitektura va Ma'lumotlar Bazasi Rejasi

Toshkent Davlat Iqtisodiyot Universiteti (TDIU / TSUE) talabalari uchun dars jadvali Telegram botining to'liq arxitekturasi va ma'lumotlar bazasi sxemasi.

Foydalanuvchi ko'rsatmasiga binoan, loyiha **faqat Telegram bot** ko'rinishida (aiogram 3 asosida) amalga oshiriladi: veb-sayt yoki tashqi veb-admin panel yo'q, barcha boshqaruv va admin amallari bevosita Telegram orqali bajariladi, faqat Docker healthcheck uchun ixcham `/health` HTTP endpointi mavjud bo'ladi. Taqdim etilgan rasmlardagi **MMT-950/26i** va **MMT-951/26i** guruhlari haqiqiy dars jadvallari bilan boshlang'ich ma'lumotlar bazasiga kiritiladi.

---

## 1. Tizim Arxitekturasi (Bot-Only)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TELEGRAM CLOUD / USERS                          │
│        (Talabalar, Guruh adminlari, O'qituvchilar, Bot Admini)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Telegram Bot API (aiogram 3)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          PYTHON BOT PROCESS                            │
│                                                                        │
│  ┌───────────────────────┐  ┌──────────────────────────────────────┐  │
│  │     Bot Handlers      │  │        Telegram Admin Panel          │  │
│  │ • /start, /help       │  │ • /admin, /stats, /users             │  │
│  │ • Guruh tanlash       │  │ • /broadcast (2-bosqichli tasdiq)    │  │
│  │ • Bugun/Ertaga/Hafta  │  │ • /sync, /backup                     │  │
│  │ • Guruh chat rejimi   │  │ • Admin ID & FSM tasdiq kodi         │  │
│  └──────────┬────────────┘  └──────────────────┬───────────────────┘  │
│             │                                  │                      │
│             ▼                                  ▼                      │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                  Middlewares & Validations                      │  │
│  │ • Anti-Flood / Rate Limiting (25 msg/s nazorati)                │  │
│  │ • i18n (O'zbek tili, lotin alifbosi)                            │  │
│  │ • Global Exception Handler (Xatolikni Adminga xabar qilish)     │  │
│  └─────────────────────────────────┬───────────────────────────────┘  │
│                                    │                                  │
│             ┌──────────────────────┴──────────────────────┐           │
│             ▼                                             ▼           │
│  ┌──────────────────────┐                     ┌────────────────────┐  │
│  │   Services & Logic   │                     │  Pillow Renderer   │  │
│  │ • Week A/B Logic     │                     │ • aSc Timetables   │  │
│  │ • Timetable Service  │────────────────────>│   dizaynida PNG    │  │
│  │ • Timetable Diff     │                     │ • TSUE logotipi    │  │
│  │ • Database Backup    │                     │ • Tur bo'yicha rang│  │
│  └──────────┬───────────┘                     │ • MD5 Kesh tizimi  │  │
│             │                                 └────────────────────┘  │
│             ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                     APScheduler (Background)                    │  │
│  │ • Darsdan 10 daqiqa oldin eslatmalar (batch, 429 retry-after)   │  │
│  │ • Guruh chatlariga har tong 07:00 da kunlik jadval jo'natish   │  │
│  │ • Kunlik SQLite .backup (arxivlash va adminga yuborish)         │  │
│  │ • Jadval sinxronizatsiyasi va o'zgarish xabarnomalari           │  │
│  └─────────────────────────────────┬───────────────────────────────┘  │
│                                    │                                  │
│             ┌──────────────────────┴──────────────────────┐           │
│             ▼                                             ▼           │
│  ┌──────────────────────┐                     ┌────────────────────┐  │
│  │   SQLite (aiosqlite) │                     │ Tiny /health HTTP  │  │
│  │ • SQLAlchemy 2.0     │                     │ • aiohttp minimal  │  │
│  │ • Alembic migration  │                     │ • Docker healtcheck│  │
│  │ • WAL rejimi         │                     │   uchun port 3000  │  │
│  └──────────────────────┘                     └────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ma'lumotlar Bazasi Sxemasi (SQLAlchemy 2.0 Async + SQLite)

SQLite ma'lumotlar bazasi tezkor va mustahkam ishlashi uchun WAL (Write-Ahead Logging) va `aiosqlite` drayveri orqali ishlaydi.

### Jadvallar:

1. **`users`**
   - `id`: BigInteger (Telegram user_id), Primary Key
   - `username`: String, nullable
   - `full_name`: String
   - `selected_group_id`: Integer, ForeignKey('groups.id'), nullable
   - `reminders_enabled`: Boolean, default=True
   - `reminder_lead_minutes`: Integer, default=10 (necha daqiqa oldin eslatish)
   - `is_active`: Boolean, default=True (botni bloklaganlarni hisobga olish)
   - `created_at`: DateTime, default=utc_now
   - `updated_at`: DateTime

2. **`faculties`**
   - `id`: Integer, Primary Key, autoincrement
   - `name`: String (Masalan: "Iqtisodiyot", "Moliya", "Xalqaro turizm")
   - `code`: String, unique

3. **`groups`**
   - `id`: Integer, Primary Key, autoincrement
   - `name`: String, unique, indexed (Masalan: `MMT-950/26i`, `MMT-951/26i`)
   - `faculty_id`: Integer, ForeignKey('faculties.id')
   - `course_year`: Integer (1, 2, 3, 4)
   - `is_active`: Boolean, default=True

4. **`teachers`**
   - `id`: Integer, Primary Key, autoincrement
   - `full_name`: String, indexed (Masalan: "Akramova Yulduz", "Ergashev O", "Xamdamov Sh")
   - `department`: String, nullable

5. **`rooms`**
   - `id`: Integer, Primary Key, autoincrement
   - `code`: String, unique, indexed (Masalan: "10-413-52", "1-bochka-220 (Moliya)", "D-ma'ruzalar zali")
   - `building`: String, nullable (Masalan: "10-bino", "Moliya instituti")

6. **`subjects`**
   - `id`: Integer, Primary Key, autoincrement
   - `name`: String, unique (Masalan: "O'zbekistonning eng yangi tarixi", "Dinshunoslik", "Amaliy matematika 1", "Rus tili", "Falsafa", "Kelajak soati Moliya 1-kurs", "Jismoniy madaniyat va Sport")

7. **`lessons`** (Dars jadvalining asosiy yozuvi)
   - `id`: Integer, Primary Key, autoincrement
   - `group_id`: Integer, ForeignKey('groups.id'), indexed
   - `subject_id`: Integer, ForeignKey('subjects.id')
   - `teacher_id`: Integer, ForeignKey('teachers.id'), nullable
   - `room_id`: Integer, ForeignKey('rooms.id'), nullable
   - `weekday`: Integer (1: Dushanba, 2: Seshanba, ..., 6: Shanba)
   - `slot_number`: Integer (1 dan 8 gacha)
   - `start_time`: Time (08:00, 09:30, 11:00, 13:00, 14:30, 16:00, 17:30, 19:00)
   - `end_time`: Time (09:20, 10:50, 12:20, 14:20, 15:50, 17:20, 18:50, 20:20)
   - `lesson_type`: String (enum: `LECTURE` (Ma), `PRACTICE` (Sem), `LAB`, `OTHER`)
   - `week_type`: String (enum: `EVERY`, `WEEK_A`, `WEEK_B`)
   - Indeks: `(group_id, weekday, slot_number, week_type)`

8. **`chat_links`** (Telegram guruh va kanallar sozlamalari)
   - `chat_id`: BigInteger, Primary Key (Telegram supergroup id)
   - `title`: String
   - `group_id`: Integer, ForeignKey('groups.id')
   - `auto_post_time`: String, default="07:00" (HH:MM formatida)
   - `is_active`: Boolean, default=True
   - `linked_by`: BigInteger (foydalanuvchi id)
   - `created_at`: DateTime

9. **`sent_reminders`** (Takroriy eslatmalarning oldini olish)
   - `id`: Integer, Primary Key, autoincrement
   - `user_id`: BigInteger
   - `lesson_id`: Integer
   - `reminder_date`: Date
   - Indeks: `(user_id, lesson_id, reminder_date)` unique

10. **`change_log`** (Jadval o'zgarishlari tarixi)
    - `id`: Integer, Primary Key, autoincrement
    - `group_id`: Integer
    - `change_type`: String (ADDED, REMOVED, MODIFIED)
    - `details`: Text (JSON formatida eski va yangi ma'lumot)
    - `created_at`: DateTime

---

## 3. Rasmda Keltirilgan 2 ta Guruh Dars Jadvali

Rasmlardagi (`MMT-951/26i` va `MMT-950/26i`) ma'lumotlar bazaga to'liq quyidagi ko'rinishda kiritiladi:

### Qo'ng'iroqlar jadvali (TSUE Standarti):
- **1-juftlik:** 08:00 – 09:20
- **2-juftlik:** 09:30 – 10:50
- **3-juftlik:** 11:00 – 12:20
- **4-juftlik:** 13:00 – 14:20
- **5-juftlik:** 14:30 – 15:50
- **6-juftlik:** 16:00 – 17:20
- **7-juftlik:** 17:30 – 18:50
- **8-juftlik:** 19:00 – 20:20

### MMT-951/26i Jadvali:
- **Dushanba:**
  - 4-para (13:00): Akramova Yulduz | O'zbekistonning eng yangi tarixi (Ma) | 10-413-52
  - 5-para (14:30): Ergashev O | Dinshunoslik (Ma) | 10-214-64
  - 6-para (16:00): Xamdamov Sh | Iqtisodiyot nazariyasi (Ma) | 10-313 (50)
- **Seshanba:**
  - 4-para (13:00): Muratova E. | Rus tili | 10-104-26
  - 5-para (14:30): Ergashev O | Dinshunoslik (Sem) | 10-213-24
  - 6-para (16:00): Egamberganova O | Amaliy matematika 1 (Ma) | 1-bochka-220 (Moliya)
  - 7-para (17:30): Sultonov Sh. | Kelajak soati Moliya 1-kurs | D-ma'ruzalar zali
- **Chorshanba:**
  - 4-para (13:00): Xamdamov Sh | Iqtisodiyot nazariyasi (Sem) | 10-310-30
  - 5-para (14:30): Qo'chqorov V | Falsafa (Ma) | 1-bochka-220 (Moliya)
- **Payshanba:**
  - 3-para (11:00): Akramova Yulduz | O'zbekistonning eng yangi tarixi (Sem) | 10-109-30
  - 4-para (13:00): Ergashev O | Falsafa (Sem) | 10-202-28
  - 5-para (14:30): Egamberganova O | Amaliy matematika 1 (Ma) | 10-305-62
- **Juma:**
  - 3-para (11:00): Egamberganova O | Amaliy matematika 1 (Sem) | 10-105-60
  - 4-para (13:00): Muratova E. | Rus tili | 10-215-64
- **Shanba:** Dars yo'q (Dam olish kuni)

### MMT-950/26i Jadvali:
- **Dushanba:**
  - 4-para (13:00): Akramova Yulduz | O'zbekistonning eng yangi tarixi (Ma) | 10-413-52
  - 5-para (14:30): Ergashev O | Dinshunoslik (Ma) | 10-214-64
  - 6-para (16:00): Xamdamov Sh | Iqtisodiyot nazariyasi (Ma) | 10-313 (50)
- **Seshanba:**
  - 4-para (13:00): Akramova Yulduz | O'zbekistonning eng yangi tarixi (Sem) | 10-211-24
  - 5-para (14:30): Xamdamov Sh | Iqtisodiyot nazariyasi (Sem) | 10-108-30
  - 6-para (16:00): Egamberganova O | Amaliy matematika 1 (Ma) | 1-bochka-220 (Moliya)
  - 7-para (17:30): Sultonov Sh. | Kelajak soati Moliya 1-kurs | D-ma'ruzalar zali
- **Chorshanba:**
  - 4-para (13:00): Ergashev O | Dinshunoslik (Sem) | 10-104-26
  - 5-para (14:30): Qo'chqorov V | Falsafa (Ma) | 1-bochka-220 (Moliya)
  - 6-para (16:00): Muratova E. | Rus tili | 10-208-40
- **Payshanba:**
  - 3-para (11:00): Ergashev O | Falsafa (Sem) | 10-108-30
  - 4-para (13:00): Muratova E. | Rus tili | 10-110-24
  - 5-para (14:30): Egamberganova O | Amaliy matematika 1 (Ma) | 10-305-62
  - 6-para (16:00): Egamberganova O | Amaliy matematika 1 (Sem) | 10-109-30
- **Juma:**
  - 1-para (08:00): RAXIMOV ABDUMALIK ABDUSATTAROVICH | Jismoniy madaniyat va Sport | Toshkent Moliya Instituti Sport kompleksi
- **Shanba:** Dars yo'q (Dam olish kuni)

---

## 4. Pillow Timetable Renderer (aSc Timetables uslubida)

Pillow orqali aynan rasmda ko'rsatilgan aSc Timetables uslubidagi chiroyli, tushunarli jadval generatsiya qilinadi:
- **O'lchamlari:** Yuqori sifatli 1400x900 px PNG.
- **Header:** TSUE logotipi, guruh nomi ("MMT-950/26i"), universitet manzili ("Tashkent State University of Economics, O'zbekiston shoh ko'chasi 49").
- **Ustunlar:** Kunlar (Mn, Tu, Wed, Thu, Fri, Sat) va 8 ta vaqt oralig'i (1 dan 8 gacha).
- **Ranglar:**
  - Ma'ruza (Ma) — sariq/binafsharang pastel fon (`#d9d2e9`, `#fff2cc`)
  - Seminar (Sem) — yashil/och qizil pastel fon (`#d9ead3`, `#f4cccc`, `#c9daf8`)
  - Jismoniy tarbiya / Sport — sariq-yashil zaytun foni (`#e6ecc5`)
- **Yozuvlar:** O'qituvchi ismi, fan nomi, xona raqami va sig'imi.
- **Kesh:** `data_hash` bo'yicha diskda keshlanadi, qayta hisoblash resurslarini tejaydi.

---

## 5. Telegram Foydalanuvchi va Admin Buyruqlari

### Foydalanuvchi interfeysi:
- `/start` — Salomlashish, guruhni tanlash (qidirish yoki inline tugmalar orqali `MMT-950/26i` yoki `MMT-951/26i`).
- `📅 Bugungi darslar` — Bugungi kun dars jadvali (matn + grafik rasm).
- `🗓 Ertangi darslar` — Ertangi kun jadvali.
- `📆 Bu haftalik jadval` — To'liq haftalik rangli aSc formatidagi PNG rasm.
- `⏭ Keyingi hafta` — A/B haftani hisobga olgan holda keyingi hafta jadvali.
- `⚙️ Sozlamalar` — Guruhni o'zgartirish, eslatmalarni yoqish/o'chirish, vaqtini belgilash (5, 10, 15 daqiqa oldin).
- `👥 Guruh chatiga qo'shish` — Botni guruhga qo'shib `/setgroup MMT-950/26i` va `/settime 07:00` orqali har tong avtomatik jadval yuborish.

### Admin interfeysi (faqat .env dagi `ADMIN_IDS` uchun):
- `/admin` — Asosiy admin menyusi (inline tugmalar).
- `/stats` — Foydalanuvchilar soni, faol guruhlar, bugun yuborilgan xabarlar statistikasi.
- `/broadcast` — Barcha foydalanuvchilarga xabar tarqatish (FSM orqali xabar kiritiladi, oldindan ko'rish va 2-bosqichli tasdiq kodi so'raladi).
- `/sync` — Jadvalni qayta tekshirish va o'zgarishlarni tekshirish.
- `/backup` — SQLite bazaning xavfsiz `.backup` nusxasini olib, arxivlangan faylni bevosita adminga jo'natish.

---

## 6. Loyiha Tuzilmasi

```
app/
├── bot/
│   ├── handlers/
│   │   ├── admin.py          # Admin buyruqlari va 2-bosqichli tasdiq
│   │   ├── common.py         # /start, /help, guruh tanlash
│   │   ├── group_chat.py     # Guruh chatlari (/setgroup, /settime)
│   │   ├── settings.py       # Eslatmalar va sozlamalar
│   │   └── timetable.py      # Bugun/ertaga/haftalik jadval yuborish
│   ├── keyboards/
│   │   ├── admin_kb.py       # Admin inline tugmalari
│   │   ├── default.py        # Asosiy menyu reply tugmalari
│   │   └── inline.py         # Guruh tanlash va ko'rish inline tugmalari
│   ├── middlewares/
│   │   ├── throttling.py     # Anti-flood middleware (25 msg/s nazorat)
│   │   └── error_handler.py  # Xatoliklarni adminga xabar qilish
│   ├── states/
│   │   └── admin_states.py   # Broadcast va admin tasdiq holatlari (FSM)
│   └── i18n/
│       └── uz.py             # Barcha matnlar va xabarlar (O'zbekcha)
├── core/
│   ├── config.py             # Pydantic-settings (.env o'qish)
│   ├── db.py                 # SQLAlchemy 2.0 async engine va session
│   ├── models.py             # Barcha jadvallar (User, Group, Lesson, ...)
│   └── logging.py            # Structured logging
├── services/
│   ├── backup.py             # SQLite online backup va arxivlash
│   ├── broadcast.py          # Xavfsiz xabar tarqatish (rate-limit, 429)
│   ├── reminders.py          # 10 daqiqa oldin eslatmalar yuborish
│   ├── renderer.py           # Pillow yordamida aSc Timetables uslubida PNG
│   ├── sync.py               # Jadval o'zgarishlarini tekshirish va diff
│   └── timetable.py          # Hafta A/B va kunlik darslarni saralash
├── providers/
│   ├── base.py               # TimetableProvider abstrakt interfeysi
│   ├── university.py         # TSUE haqiqiy integratsiya provayderi (stub)
│   └── tsue_seeded.py        # MMT-950/26i va MMT-951/26i haqiqiy jadvallari
├── scheduler.py              # APScheduler joblari (eslatmalar, tonggi jadval)
├── health.py                 # Ixcham /health HTTP serveri (port 3000)
└── main.py                   # Asosiy ishga tushirish fayli
Dockerfile
docker-compose.yml
.env.example
README.md
tests/
  ├── test_week_logic.py      # A/B hafta hisoblash testlari
  ├── test_renderer.py        # Pillow rasm chizish testlari
  └── test_diff_logic.py      # Jadval o'zgarishini aniqlash testlari
```

---

## 7. Ishga Tushirish va Joylashtirish (AWS EC2 / Docker)

- **Docker:** Multi-stage `python:3.12-slim` imij, SQLite va rasm keshi uchun `volumes: - ./data:/app/data`.
- **Healthcheck:** Docker compose sog'liqni tekshirish uchun `http://localhost:3000/health` endpointidan foydalanadi.
- **AWS EC2:** Ubuntu 22.04/24.04, Docker + Docker Compose, systemd servis yoki `restart: always` orqali 24/7 uzluksiz ishlash ta'minlanadi.

---

Iltimos, ushbu arxitektura va ma'lumotlar bazasi rejasini ko'rib chiqing. Tasdiqlasangiz, darhol to'liq kodni bosqichma-bosqich ishlab chiqishga kirishamiz.
