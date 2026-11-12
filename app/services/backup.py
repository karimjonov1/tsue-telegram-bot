import os
import gzip
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from aiogram import Bot
from aiogram.types import FSInputFile

from app.core.config import settings
from app.core.logging import logger


def perform_sqlite_backup() -> str:
    """
    Safely backup the SQLite database using SQLite's online backup API,
    then compress with gzip.
    Returns the path to the compressed backup file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_source_path = settings.DATA_DIR + "/tsue_bot.db"
    backup_raw_path = os.path.join(settings.BACKUP_DIR, f"tsue_bot_{timestamp}.db")
    backup_gz_path = f"{backup_raw_path}.gz"

    if not os.path.exists(db_source_path):
        raise FileNotFoundError(f"Database file not found at {db_source_path}")

    # Use SQLite's safe online backup API
    src_conn = sqlite3.connect(db_source_path)
    dst_conn = sqlite3.connect(backup_raw_path)
    with dst_conn:
        src_conn.backup(dst_conn, pages=100)
    dst_conn.close()
    src_conn.close()

    # Compress with gzip
    with open(backup_raw_path, 'rb') as f_in:
        with gzip.open(backup_gz_path, 'wb', compresslevel=9) as f_out:
            shutil.copyfileobj(f_in, f_out)

    # Remove uncompressed raw backup
    os.remove(backup_raw_path)
    logger.info(f"Safe SQLite backup created: {backup_gz_path}")

    # Rotate old backups
    rotate_backups(settings.BACKUP_DIR, settings.BACKUP_RETENTION_COUNT)

    return backup_gz_path


def rotate_backups(backup_dir: str, keep_count: int = 7) -> None:
    """Keep only the latest N backup files and delete older ones."""
    p = Path(backup_dir)
    files = sorted(p.glob("tsue_bot_*.db.gz"), key=lambda f: f.stat().st_mtime)
    if len(files) > keep_count:
        to_delete = files[:-keep_count]
        for f in to_delete:
            try:
                f.unlink()
                logger.info(f"Deleted old backup: {f.name}")
            except Exception as e:
                logger.error(f"Failed to delete old backup {f.name}: {e}")


async def create_and_send_backup(bot: Bot, target_chat_id: int) -> str:
    """Generate backup and send it directly to the Telegram admin/channel."""
    backup_path = perform_sqlite_backup()
    file_size_kb = os.path.getsize(backup_path) / 1024.0
    caption = (
        f"💾 <b>TSUE Bot Ma'lumotlar Bazasi Zaxira Nusxasi (Backup)</b>\n\n"
        f"📅 Sana: <b>{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</b>\n"
        f"📦 Hajmi: <b>{file_size_kb:.2f} KB</b>\n"
        f"🔒 Format: SQLite 3 (Gzip siqilgan)"
    )
    document = FSInputFile(backup_path)
    await bot.send_document(
        chat_id=target_chat_id,
        document=document,
        caption=caption,
        parse_mode="HTML"
    )
    return backup_path
