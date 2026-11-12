import sys
import csv
import asyncio
from pathlib import Path
from sqlalchemy import select
from app.core.db import AsyncSessionLocal, init_db
from app.core.models import Group, Teacher, Room, Subject, Lesson
from app.core.logging import logger
from app.providers.tsue_seeded import TSUEImageSeededProvider


async def import_timetable_csv(csv_path: str) -> int:
    """
    Import timetable from a CSV file.
    Expected headers: group,weekday,slot,teacher,subject,room,lesson_type,week_type
    """
    await init_db()
    path = Path(csv_path)
    if not path.exists():
        logger.error(f"File not found: {csv_path}")
        return 0

    inserted_count = 0
    slot_times = TSUEImageSeededProvider.SLOT_TIMES

    async with AsyncSessionLocal() as session:
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                group_name = row["group"].strip()
                weekday = int(row["weekday"].strip())
                slot = int(row["slot"].strip())
                teacher_name = row.get("teacher", "").strip()
                subject_name = row["subject"].strip()
                room_code = row.get("room", "").strip()
                lesson_type = row.get("lesson_type", "Ma").strip()
                week_type = row.get("week_type", "EVERY").strip()

                # Get or create Group
                res = await session.execute(select(Group).where(Group.name.ilike(group_name)))
                group = res.scalars().first()
                if not group:
                    group = Group(name=group_name)
                    session.add(group)
                    await session.flush()

                # Get or create Subject
                res = await session.execute(select(Subject).where(Subject.name == subject_name))
                subject = res.scalars().first()
                if not subject:
                    subject = Subject(name=subject_name)
                    session.add(subject)
                    await session.flush()

                # Get or create Teacher
                teacher = None
                if teacher_name:
                    res = await session.execute(select(Teacher).where(Teacher.full_name == teacher_name))
                    teacher = res.scalars().first()
                    if not teacher:
                        teacher = Teacher(full_name=teacher_name)
                        session.add(teacher)
                        await session.flush()

                # Get or create Room
                room = None
                if room_code:
                    res = await session.execute(select(Room).where(Room.code == room_code))
                    room = res.scalars().first()
                    if not room:
                        room = Room(code=room_code)
                        session.add(room)
                        await session.flush()

                start_t, end_t = slot_times.get(slot, ("08:00", "09:20"))

                # Check if lesson exists
                res = await session.execute(
                    select(Lesson).where(
                        Lesson.group_id == group.id,
                        Lesson.weekday == weekday,
                        Lesson.slot_number == slot,
                        Lesson.week_type == week_type
                    )
                )
                existing = res.scalars().first()
                if not existing:
                    lesson = Lesson(
                        group_id=group.id,
                        subject_id=subject.id,
                        teacher_id=teacher.id if teacher else None,
                        room_id=room.id if room else None,
                        weekday=weekday,
                        slot_number=slot,
                        start_time=start_t,
                        end_time=end_t,
                        lesson_type=lesson_type,
                        week_type=week_type
                    )
                    session.add(lesson)
                    inserted_count += 1

        await session.commit()
    logger.info(f"Successfully imported {inserted_count} lessons from {csv_path}")
    return inserted_count


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.scripts.import_csv <path_to_csv>")
        sys.exit(1)
    asyncio.run(import_timetable_csv(sys.argv[1]))
