# TSUE Dars Jadvali Telegram Bot

Production-ready Telegram bot for students of **Tashkent State University of Economics (TSUE / TDIU)**. Built with Python 3.12, aiogram 3, SQLite (SQLAlchemy 2.0 Async + aiosqlite), APScheduler, and Pillow for timetable rendering.

All user-facing messages are in **Uzbek (Latin script)** via a centralized i18n module.

---

## 📸 Generated Timetable Samples
Pre-seeded with real schedules for **MMT-950/26i** and **MMT-951/26i** (Finance & Banking Faculty):
- `public/samples/timetable_MMT_950_26i.png`
- `public/samples/timetable_MMT_951_26i.png`

Rendered in the exact **aSc Timetables** visual style with TSUE official emblem, pastel color coding for lectures, seminars, and physical training, teacher names, and room codes.

---

## 🚀 Key Features

1. **Timetable Views (Text + PNG Images):**
   - `📅 Bugungi darslar`: Today's lessons formatted in clean Uzbek text with room codes and teachers.
   - `🗓 Ertangi darslar`: Tomorrow's lessons.
   - `📆 Bu haftalik jadval`: High-resolution PNG generated with Pillow and cached by entity, week, and data hash.
   - `⏭ Keyingi hafta`: Next week's schedule according to alternating Week A/B logic.

2. **Week A / Week B Support:**
   - Odd / even week alternation calculated from a configurable semester start date (`2026-09-07`).
   - Lessons can be flagged `EVERY`, `WEEK_A` only, or `WEEK_B` only.

3. **Intelligent Reminders:**
   - Automatic notification sent 10 minutes (configurable to 5, 10, 15, 30 min) before each lesson starts.
   - Duplicate prevention via `sent_reminders` tracking table.
   - Throttled batch dispatcher handling Telegram API limits (~25 msg/s), 429 `Retry-After`, and deactivated/blocked users.

4. **Telegram Group Chat Support:**
   - Add bot to a student group chat and configure it with:
     - `/setgroup MMT-950/26i` — Links group.
     - `/settime 07:00` — Sets morning timetable delivery time.
     - `/stop` — Stops automatic posts.
   - Restricts configuration to chat administrators.

5. **In-Bot Telegram Admin Panel:**
   - Accessible only by IDs configured in `ADMIN_IDS`:
     - `/admin` — Interactive admin dashboard with inline buttons.
     - `/stats` — Real-time metrics: active users, total groups, linked group chats, lessons count, today's reminder deliveries.
     - `/users` — Recent registrations and user statuses.
     - `/broadcast` — Mass messaging with a **2-step verification code** (e.g. 4-digit security code) to prevent accidental sends.
     - `/sync` — Manual timetable sync and diff check.
     - `/backup` — Performs online SQLite `.backup`, compresses with gzip, and sends the `.db.gz` file directly into Telegram!

6. **Pluggable Data Providers:**
   - `TSUEImageSeededProvider`: Seeded with exact official timetable data for MMT-950/26i and MMT-951/26i.
   - `UniversityAPIProvider`: Stub for future TSUE HEMIS / aSc Timetables API integration with clear TODO markers.
   - `import_csv.py`: CSV import CLI script for batch importing lessons.

7. **Healthcheck & Monitoring:**
   - Lightweight `aiohttp` HTTP server on port 3000 providing `/health` for Docker container monitoring and uptime probes.

---

## 🛠 Project Structure

```
├── app/
│   ├── main.py                  # Entry point (bot polling, scheduler, health server)
│   ├── scheduler.py             # APScheduler jobs (reminders, morning posts, backup)
│   ├── health.py                # Lightweight /health HTTP server (port 3000)
│   ├── core/
│   │   ├── config.py            # Pydantic-settings (.env loader)
│   │   ├── db.py                # Async SQLite engine (WAL mode)
│   │   ├── models.py            # SQLAlchemy 2.0 models
│   │   └── logging.py           # Structured logging
│   ├── bot/
│   │   ├── i18n/
│   │   │   └── uz.py            # Uzbek language strings (Latin script)
│   │   ├── keyboards/
│   │   │   ├── default.py       # Main reply keyboard
│   │   │   ├── inline.py        # Group selection and settings inline keyboards
│   │   │   └── admin_kb.py      # Admin panel inline keyboard
│   │   ├── middlewares/
│   │   │   ├── throttling.py    # Anti-flood rate limiting
│   │   │   └── error_handler.py # Global error reporting to admin
│   │   ├── states/
│   │   │   └── admin_states.py  # FSM state machine for broadcast confirmation
│   │   └── handlers/
│   │       ├── common.py        # /start, /help, group selector
│   │       ├── timetable.py     # Today, tomorrow, week, next week handlers
│   │       ├── settings.py      # Reminder settings
│   │       ├── group_chat.py    # Group chat commands (/setgroup, /settime, /stop)
│   │       └── admin.py         # Admin commands (/admin, /stats, /broadcast, /backup)
│   ├── services/
│   │   ├── timetable.py         # Week A/B logic, lesson queries, text formatter
│   │   ├── renderer.py          # Pillow aSc Timetables PNG renderer & cache
│   │   ├── reminders.py         # Lesson reminders dispatcher
│   │   ├── sync.py              # Timetable diff engine & cache invalidator
│   │   ├── backup.py            # SQLite online backup & gzip compression
│   │   └── broadcast.py         # Batch message broadcast engine
│   ├── providers/
│   │   ├── base.py              # TimetableProvider ABC
│   │   ├── tsue_seeded.py       # MMT-950/26i & MMT-951/26i timetable data
│   │   └── university.py        # University API stub
│   └── scripts/
│       ├── seed_db.py           # Database initial seeder
│       └── import_csv.py        # CSV import script
├── tests/                       # Pytest test suite
├── Dockerfile                   # Python 3.12-slim production Dockerfile
├── docker-compose.yml           # Compose specification with healthcheck & volume
├── requirements.txt             # Python dependencies
└── .env.example                 # Configuration template
```

---

## 💻 Local Quickstart

### 1. Prerequisites
- Python 3.11 or 3.12
- SQLite 3
- TTF fonts (`fonts-liberation` or `fonts-dejavu-core`)

### 2. Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure `.env`
```bash
cp .env.example .env
# Edit .env with your BOT_TOKEN from @BotFather and your ADMIN_IDS
```

### 4. Run Unit Tests
```bash
pytest -v
```

### 5. Start the Bot
```bash
python -m app.main
```

---

## 🐳 Running with Docker

### 1. Build and Run Container
```bash
docker compose up -d --build
```

### 2. Check Logs
```bash
docker compose logs -f tsue_bot
```

### 3. Verify Health Check
```bash
curl http://localhost:3000/health
# Returns: {"status": "healthy", "service": "tsue_telegram_bot", ...}
```

---

## ☁️ Step-by-Step AWS EC2 Deployment Guide

### 1. Launch EC2 Instance
- **AMI:** Ubuntu 22.04 LTS or Ubuntu 24.04 LTS (x86_64)
- **Instance Type:** `t3.micro` or `t3.small` (t3.micro with 1GB RAM is sufficient for SQLite + bot)
- **Storage:** 20 GB gp3 EBS Volume
- **Security Group Inbound Rules:**
  - SSH: Port 22 (restricted to your IP)
  - HTTP: Port 3000 (for health checks or internal VPC monitoring)

### 2. Connect & Install Docker Engine
```bash
ssh -i "your-key.pem" ubuntu@<your-ec2-public-ip>

# Update and install Docker & Docker Compose
sudo apt-get update && sudo apt-get install -y ca-certificates curl gnupg git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker ubuntu
```
*(Log out and log back in for docker group changes to take effect).*

### 3. Clone Repository & Setup Environment
```bash
git clone <your-repository-url> /home/ubuntu/tsue-bot
cd /home/ubuntu/tsue-bot

cp .env.example .env
nano .env
```
Provide your actual `BOT_TOKEN` from `@BotFather` and your numeric Telegram ID in `ADMIN_IDS`.

### 4. Start via Docker Compose
```bash
docker compose up -d --build
```

The container starts with `restart: always`, ensuring it automatically reboots if the EC2 instance restarts or crashes.

### 5. Automated Backups & System Monitoring
- Backups are automatically generated every day at 03:00 AM by APScheduler and sent directly to your Telegram admin chat.
- You can manually trigger a backup at any time by messaging `/backup` to your bot.
