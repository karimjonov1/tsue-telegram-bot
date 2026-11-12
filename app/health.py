import json
import os
from datetime import datetime
from aiohttp import web
from app.core.config import settings
from app.core.logging import logger


async def health_check_handler(request: web.Request) -> web.Response:
    """Tiny healthcheck endpoint for Docker container / health checks."""
    data = {
        "status": "healthy",
        "service": "tsue_telegram_bot",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "groups_supported": ["MMT-950/26i", "MMT-951/26i"]
    }
    return web.json_response(data, status=200)


async def web_info_handler(request: web.Request) -> web.Response:
    """HTML preview and health status page."""
    html_content = f"""<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TSUE Dars Jadvali Telegram Bot</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 24px; margin-bottom: 24px; border: 1px solid #334155; }}
        h1 {{ color: #38bdf8; margin-top: 0; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 13px; font-weight: 600; background: #10b981; color: white; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
        .item {{ background: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; }}
        code {{ background: #334155; padding: 2px 6px; border-radius: 4px; color: #38bdf8; font-size: 13px; }}
        img.preview {{ width: 100%; border-radius: 8px; margin-top: 12px; border: 1px solid #475569; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🏛 TSUE Dars Jadvali Telegram Bot</h1>
            <p><span class="badge">ONLINE / ISHLAMOQDA</span> &nbsp; • &nbsp; Port: <code>{settings.HEALTH_PORT}</code> &nbsp; • &nbsp; Healthcheck: <code>/health</code></p>
            <p>Toshkent Davlat Iqtisodiyot Universiteti (TDIU) talabalari uchun dars jadvali, eslatmalar va guruh chatlari Telegram boti.</p>
        </div>

        <div class="card">
            <h2>📚 Birlamchi Guruhlar va Dars Jadvallari:</h2>
            <div class="grid">
                <div class="item">
                    <h3>🏛 MMT-950/26i</h3>
                    <p>Fakultet: <b>Moliya va Bank ishi (1-kurs)</b></p>
                    <p>Hafta formati: <b>A/B Hafta (Toq/Juft)</b></p>
                    <a href="/samples/timetable_MMT_950_26i.png" target="_blank" style="color:#38bdf8; text-decoration: none;">🖼 Jadval rasmini ko'rish (PNG)</a>
                </div>
                <div class="item">
                    <h3>🏛 MMT-951/26i</h3>
                    <p>Fakultet: <b>Moliya va Bank ishi (1-kurs)</b></p>
                    <p>Hafta formati: <b>A/B Hafta (Toq/Juft)</b></p>
                    <a href="/samples/timetable_MMT_951_26i.png" target="_blank" style="color:#38bdf8; text-decoration: none;">🖼 Jadval rasmini ko'rish (PNG)</a>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🤖 Telegram Bot Buyruqlari:</h2>
            <ul>
                <li><code>/start</code> — Botni ishga tushirish va guruh tanlash</li>
                <li><code>/help</code> — Yordam va qo'llanma</li>
                <li><code>/setgroup &lt;Guruh&gt;</code> — Telegram guruh chatiga biriktirish (masalan: <code>/setgroup MMT-950/26i</code>)</li>
                <li><code>/settime &lt;HH:MM&gt;</code> — Tonggi avtomatik jadval vaqtini belgilash (masalan: <code>/settime 07:00</code>)</li>
                <li><code>/admin</code> — Admin paneli (faqat adminlar uchun)</li>
                <li><code>/backup</code> — SQLite bazani zaxiralash va telegramga yuborish</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
    return web.Response(text=html_content, content_type="text/html")


def start_health_server(port: int = 3000) -> web.AppRunner:
    """Create and start lightweight aiohttp application."""
    app = web.Application()
    app.router.add_get("/health", health_check_handler)
    app.router.add_get("/", web_info_handler)
    # Serve static samples if available
    if os.path.exists("public/samples"):
        app.router.add_static("/samples", "public/samples")
    
    runner = web.AppRunner(app)
    return runner
