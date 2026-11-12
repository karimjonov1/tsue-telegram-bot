import asyncio
import signal
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

from app.core.config import settings
from app.core.logging import logger
from app.core.db import init_db
from app.scripts.seed_db import seed_database
from app.bot.handlers import common, timetable, settings as bot_settings, group_chat, admin
from app.bot.middlewares.throttling import ThrottlingMiddleware
from app.bot.middlewares.error_handler import GlobalErrorHandlerMiddleware
from app.scheduler import setup_scheduler
from app.health import start_health_server


async def main() -> None:
    logger.info("Initializing TSUE Telegram Bot...")

    # 1. Initialize SQLite Database & seed TSUE timetable
    await init_db()
    await seed_database()

    # 2. Start Health Check HTTP server
    health_runner = start_health_server(port=settings.HEALTH_PORT)
    await health_runner.setup()
    try:
        site = web.TCPSite(health_runner, "0.0.0.0", settings.HEALTH_PORT)
        await site.start()
        logger.info(f"Health server listening on http://0.0.0.0:{settings.HEALTH_PORT}/health")
    except OSError:
        # Port 3000 may be used by Vite dev server in this environment, try port 3001
        fallback_port = 3001
        site = web.TCPSite(health_runner, "0.0.0.0", fallback_port)
        await site.start()
        logger.info(f"Health server listening on fallback port http://0.0.0.0:{fallback_port}/health")

    # 3. Check Telegram Bot Token
    token = settings.BOT_TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        logger.warning(
            "===============================================================\n"
            "⚠️ BOT_TOKEN is not configured in .env!\n"
            "The healthcheck server is running on port 3000.\n"
            "To connect to Telegram, provide BOT_TOKEN in .env file or environment variable.\n"
            "==============================================================="
        )
        # Keep process alive so Docker / healthcheck continues to function
        while True:
            await asyncio.sleep(3600)

    # 4. Initialize Bot & Dispatcher
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    # 5. Register Middlewares
    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.4))
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.4))
    dp.message.middleware(GlobalErrorHandlerMiddleware(bot))
    dp.callback_query.middleware(GlobalErrorHandlerMiddleware(bot))

    # 6. Register Routers
    dp.include_router(admin.router)
    dp.include_router(group_chat.router)
    dp.include_router(bot_settings.router)
    dp.include_router(timetable.router)
    dp.include_router(common.router)

    # 7. Start Scheduler
    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("APScheduler background tasks started.")

    # 8. Start Polling
    try:
        logger.info("Starting bot long polling...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down bot...")
        scheduler.shutdown()
        await health_runner.cleanup()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
