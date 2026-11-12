import asyncio
from sqlalchemy import select
from app.core.db import AsyncSessionLocal, init_db
from app.core.models import Faculty, Group, Teacher, Room, Subject, Lesson
from app.providers.tsue_seeded import TSUEImageSeededProvider
from app.core.logging import logger


async def seed_database() -> None:
    """Seed SQLite database with TSUE faculties, groups, and lessons."""
    await init_db()
    provider = TSUEImageSeededProvider()

    async with AsyncSessionLocal() as session:
        # 1. Create or get Faculty
        faculty_name = "Moliya va Bank ishi"
        res = await session.execute(select(Faculty).where(Faculty.code == "MBI"))
        faculty = res.scalars().first()
        if not faculty:
            faculty = Faculty(name=faculty_name, code="MBI")
            session.add(faculty)
            await session.flush()

        # 2. Seed Groups
        groups_dict = {}
        for g_data in provider.GROUPS:
            res = await session.execute(select(Group).where(Group.name == g_data["name"]))
            group = res.scalars().first()
            if not group:
                group = Group(
                    name=g_data["name"],
                    faculty_id=faculty.id,
                    course_year=g_data["course"],
                    is_active=True
                )
                session.add(group)
                await session.flush()
            groups_dict[group.name] = group

        # 3. Seed Teachers
        teachers_dict = {}
        for teacher_name in await provider.fetch_teachers():
            res = await session.execute(select(Teacher).where(Teacher.full_name == teacher_name))
            teacher = res.scalars().first()
            if not teacher:
                teacher = Teacher(full_name=teacher_name)
                session.add(teacher)
                await session.flush()
            teachers_dict[teacher_name] = teacher

        # 4. Seed Rooms
        rooms_dict = {}
        for room_code in await provider.fetch_rooms():
            res = await session.execute(select(Room).where(Room.code == room_code))
            room = res.scalars().first()
            if not room:
                room = Room(code=room_code)
                session.add(room)
                await session.flush()
            rooms_dict[room_code] = room

        # 5. Seed Lessons
        lessons_dto = await provider.fetch_lessons()
        subjects_dict = {}

        for l_dto in lessons_dto:
            # Check subject
            if l_dto.subject_name not in subjects_dict:
                res = await session.execute(select(Subject).where(Subject.name == l_dto.subject_name))
                subj = res.scalars().first()
                if not subj:
                    subj = Subject(name=l_dto.subject_name)
                    session.add(subj)
                    await session.flush()
                subjects_dict[l_dto.subject_name] = subj

            group = groups_dict[l_dto.group_name]
            subj = subjects_dict[l_dto.subject_name]
            teacher = teachers_dict.get(l_dto.teacher_name)
            room = rooms_dict.get(l_dto.room_code)

            # Check if lesson already exists
            res = await session.execute(
                select(Lesson).where(
                    Lesson.group_id == group.id,
                    Lesson.weekday == l_dto.weekday,
                    Lesson.slot_number == l_dto.slot_number,
                    Lesson.week_type == l_dto.week_type
                )
            )
            existing_lesson = res.scalars().first()
            if not existing_lesson:
                lesson = Lesson(
                    group_id=group.id,
                    subject_id=subj.id,
                    teacher_id=teacher.id if teacher else None,
                    room_id=room.id if room else None,
                    weekday=l_dto.weekday,
                    slot_number=l_dto.slot_number,
                    start_time=l_dto.start_time,
                    end_time=l_dto.end_time,
                    lesson_type=l_dto.lesson_type,
                    week_type=l_dto.week_type
                )
                session.add(lesson)

        await session.commit()
        logger.info("Database successfully seeded with TSUE groups and timetables!")


if __name__ == "__main__":
    asyncio.run(seed_database())
