import os
import pytest
from datetime import date
from app.core.db import init_db
from app.scripts.seed_db import seed_database
from app.services.timetable import get_group_by_name, get_lessons_for_full_week
from app.services.renderer import render_timetable_image


@pytest.mark.asyncio
async def test_pillow_rendering():
    await init_db()
    await seed_database()

    group = await get_group_by_name("MMT-950/26i")
    assert group is not None

    lessons_by_day, week_type, monday, saturday = await get_lessons_for_full_week(
        group.id, date(2026, 9, 14)
    )
    assert len(lessons_by_day[1]) >= 3  # Monday lessons

    image_path = await render_timetable_image(group.name, lessons_by_day, week_type)
    assert os.path.exists(image_path)
    assert os.path.getsize(image_path) > 10000  # Valid non-empty PNG
