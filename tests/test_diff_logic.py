import pytest
from app.providers.base import TimetableProvider, LessonDTO
from app.services.sync import diff_and_sync_timetable
from app.core.db import init_db
from app.scripts.seed_db import seed_database


class MockChangingProvider(TimetableProvider):
    def __init__(self, lessons):
        self.lessons = lessons

    async def fetch_groups(self):
        return [{"name": "MMT-950/26i", "course": 1, "faculty": "Moliya"}]

    async def fetch_lessons(self, group_name=None):
        return self.lessons

    async def fetch_teachers(self):
        return []

    async def fetch_rooms(self):
        return []


@pytest.mark.asyncio
async def test_timetable_diff_detection():
    await init_db()
    await seed_database()

    # Create modified lesson
    modified_lessons = [
        LessonDTO(
            group_name="MMT-950/26i",
            subject_name="O'zbekistonning eng yangi tarixi",
            teacher_name="Akramova Yulduz",
            room_code="10-999-99",  # CHANGED ROOM
            weekday=1,
            slot_number=4,
            start_time="13:00",
            end_time="14:20",
            lesson_type="Ma",
            week_type="EVERY"
        )
    ]
    provider = MockChangingProvider(modified_lessons)
    result = await diff_and_sync_timetable(provider, bot=None)

    assert result["groups_checked"] == 1
    assert "MMT-950/26I" in result["changes_detected"]
    changes = result["changes_detected"]["MMT-950/26I"]
    assert any("O'zgardi" in c or "10-999-99" in c for c in changes)
