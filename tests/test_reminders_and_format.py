import pytest
from datetime import date
from app.core.db import init_db
from app.scripts.seed_db import seed_database
from app.services.timetable import (
    get_group_by_name,
    get_lessons_for_day,
    format_day_schedule_text
)


@pytest.mark.asyncio
async def test_schedule_text_formatting():
    await init_db()
    await seed_database()

    group = await get_group_by_name("MMT-951/26i")
    assert group is not None

    # Test Monday lessons
    monday_date = date(2026, 9, 7)
    lessons, week_type = await get_lessons_for_day(group.id, monday_date)
    assert len(lessons) >= 3

    text = format_day_schedule_text(
        group_name=group.name,
        target_date=monday_date,
        lessons=lessons,
        week_type=week_type,
        is_tomorrow=False
    )

    # Check key text components in Uzbek
    assert "MMT-951/26i" in text
    assert "Dushanba" in text
    assert "O'zbekistonning eng yangi tarixi" in text
    assert "Dinshunoslik" in text
    assert "Iqtisodiyot nazariyasi" in text
    assert "10-413-52" in text
