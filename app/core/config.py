from typing import List
import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    BOT_TOKEN: str = Field(default="YOUR_BOT_TOKEN_HERE", description="Telegram Bot API Token")
    ADMIN_IDS_STR: str = Field(default="123456789", alias="ADMIN_IDS", description="Comma-separated Telegram user IDs")
    
    DB_URL: str = Field(
        default="sqlite+aiosqlite:///./data/tsue_bot.db",
        description="Async SQLite database connection string"
    )
    SYNC_DB_URL: str = Field(
        default="sqlite:///./data/tsue_bot.db",
        description="Sync SQLite URL for Alembic or backup"
    )
    
    # Semester start date for Week A/B alternating calculation
    # Format: YYYY-MM-DD. Image specifies validity starting 2026-09-07
    SEMESTER_START_DATE: str = Field(default="2026-09-07", description="Semester start date YYYY-MM-DD")
    
    DEFAULT_REMINDER_LEAD_MINUTES: int = Field(default=10, description="Lead time for reminders before lesson")
    DATA_DIR: str = Field(default="./data", description="Data directory for SQLite and backups")
    CACHE_DIR: str = Field(default="./data/cache", description="Cache directory for rendered images")
    BACKUP_DIR: str = Field(default="./data/backups", description="Directory to store compressed backups")
    
    # Backup retention count
    BACKUP_RETENTION_COUNT: int = Field(default=7, description="Number of daily backups to keep locally")
    
    # Health check server port
    HEALTH_PORT: int = Field(default=3000, description="Lightweight healthcheck port")
    
    # Optional webhook url
    WEBHOOK_URL: str = Field(default="", description="Webhook URL if using webhooks instead of long polling")

    @property
    def admin_ids(self) -> List[int]:
        ids: List[int] = []
        for x in self.ADMIN_IDS_STR.split(","):
            val = x.strip()
            if val.isdigit() or (val.startswith("-") and val[1:].isdigit()):
                ids.append(int(val))
        return ids


settings = Settings()

# Ensure directories exist
Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.CACHE_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.BACKUP_DIR).mkdir(parents=True, exist_ok=True)
