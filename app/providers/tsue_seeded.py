from typing import List, Dict, Any, Optional
from app.providers.base import TimetableProvider, LessonDTO


class TSUEImageSeededProvider(TimetableProvider):
    """
    Timetable provider initialized with real data directly extracted from
    Tashkent State University of Economics (TSUE) official timetable images:
    MMT-950/26i and MMT-951/26i.
    """

    SLOT_TIMES = {
        1: ("08:00", "09:20"),
        2: ("09:30", "10:50"),
        3: ("11:00", "12:20"),
        4: ("13:00", "14:20"),
        5: ("14:30", "15:50"),
        6: ("16:00", "17:20"),
        7: ("17:30", "18:50"),
        8: ("19:00", "20:20"),
    }

    GROUPS = [
        {"name": "MMT-950/26i", "course": 1, "faculty": "Moliya va Bank ishi"},
        {"name": "MMT-951/26i", "course": 1, "faculty": "Moliya va Bank ishi"},
    ]

    # Raw definitions: (group, weekday, slot, teacher, subject, room, type, week_type)
    RAW_LESSONS = [
        # === MMT-950/26i ===
        # Monday (1)
        ("MMT-950/26i", 1, 4, "Akramova Yulduz", "O'zbekistonning eng yangi tarixi", "10-413-52", "Ma", "EVERY"),
        ("MMT-950/26i", 1, 5, "Ergashev O", "Dinshunoslik", "10-214-64", "Ma", "EVERY"),
        ("MMT-950/26i", 1, 6, "Xamdamov Sh", "Iqtisodiyot nazariyasi", "10-313 (50)", "Ma", "EVERY"),
        # Tuesday (2)
        ("MMT-950/26i", 2, 4, "Akramova Yulduz", "O'zbekistonning eng yangi tarixi", "10-211-24", "Sem", "EVERY"),
        ("MMT-950/26i", 2, 5, "Xamdamov Sh", "Iqtisodiyot nazariyasi", "10-108-30", "Sem", "EVERY"),
        ("MMT-950/26i", 2, 6, "Egamberganova O", "Amaliy matematika 1", "1-bochka-220 (Moliya)", "Ma", "EVERY"),
        ("MMT-950/26i", 2, 7, "Sultonov Sh.", "Kelajak soati Moliya 1-kurs", "D-ma'ruzalar zali", "Ma", "EVERY"),
        # Wednesday (3)
        ("MMT-950/26i", 3, 4, "Ergashev O", "Dinshunoslik", "10-104-26", "Sem", "EVERY"),
        ("MMT-950/26i", 3, 5, "Qo'chqorov V", "Falsafa", "1-bochka-220 (Moliya)", "Ma", "EVERY"),
        ("MMT-950/26i", 3, 6, "Muratova E.", "Rus tili", "10-208-40", "Sem", "EVERY"),
        # Thursday (4)
        ("MMT-950/26i", 4, 3, "Ergashev O", "Falsafa", "10-108-30", "Sem", "EVERY"),
        ("MMT-950/26i", 4, 4, "Muratova E.", "Rus tili", "10-110-24", "Sem", "EVERY"),
        ("MMT-950/26i", 4, 5, "Egamberganova O", "Amaliy matematika 1", "10-305-62", "Ma", "EVERY"),
        ("MMT-950/26i", 4, 6, "Egamberganova O", "Amaliy matematika 1", "10-109-30", "Sem", "EVERY"),
        # Friday (5)
        ("MMT-950/26i", 5, 1, "RAXIMOV ABDUMALIK ABDUSATTAROVICH", "Jismoniy madaniyat va Sport", "Toshkent Moliya Instituti Sport kompleksi", "Sport", "EVERY"),

        # === MMT-951/26i ===
        # Monday (1)
        ("MMT-951/26i", 1, 4, "Akramova Yulduz", "O'zbekistonning eng yangi tarixi", "10-413-52", "Ma", "EVERY"),
        ("MMT-951/26i", 1, 5, "Ergashev O", "Dinshunoslik", "10-214-64", "Ma", "EVERY"),
        ("MMT-951/26i", 1, 6, "Xamdamov Sh", "Iqtisodiyot nazariyasi", "10-313 (50)", "Ma", "EVERY"),
        # Tuesday (2)
        ("MMT-951/26i", 2, 4, "Muratova E.", "Rus tili", "10-104-26", "Sem", "EVERY"),
        ("MMT-951/26i", 2, 5, "Ergashev O", "Dinshunoslik", "10-213-24", "Sem", "EVERY"),
        ("MMT-951/26i", 2, 6, "Egamberganova O", "Amaliy matematika 1", "1-bochka-220 (Moliya)", "Ma", "EVERY"),
        ("MMT-951/26i", 2, 7, "Sultonov Sh.", "Kelajak soati Moliya 1-kurs", "D-ma'ruzalar zali", "Ma", "EVERY"),
        # Wednesday (3)
        ("MMT-951/26i", 3, 4, "Xamdamov Sh", "Iqtisodiyot nazariyasi", "10-310-30", "Sem", "EVERY"),
        ("MMT-951/26i", 3, 5, "Qo'chqorov V", "Falsafa", "1-bochka-220 (Moliya)", "Ma", "EVERY"),
        # Thursday (4)
        ("MMT-951/26i", 4, 3, "Akramova Yulduz", "O'zbekistonning eng yangi tarixi", "10-109-30", "Sem", "EVERY"),
        ("MMT-951/26i", 4, 4, "Ergashev O", "Falsafa", "10-202-28", "Sem", "EVERY"),
        ("MMT-951/26i", 4, 5, "Egamberganova O", "Amaliy matematika 1", "10-305-62", "Ma", "EVERY"),
        # Friday (5)
        ("MMT-951/26i", 5, 3, "Egamberganova O", "Amaliy matematika 1", "10-105-60", "Sem", "EVERY"),
        ("MMT-951/26i", 5, 4, "Muratova E.", "Rus tili", "10-215-64", "Sem", "EVERY"),
    ]

    async def fetch_groups(self) -> List[Dict[str, Any]]:
        return self.GROUPS

    async def fetch_lessons(self, group_name: Optional[str] = None) -> List[LessonDTO]:
        result = []
        for g, w, s, teacher, subj, room, ltype, wtype in self.RAW_LESSONS:
            if group_name and g.upper() != group_name.upper():
                continue
            start_t, end_t = self.SLOT_TIMES[s]
            result.append(
                LessonDTO(
                    group_name=g,
                    subject_name=subj,
                    teacher_name=teacher,
                    room_code=room,
                    weekday=w,
                    slot_number=s,
                    start_time=start_t,
                    end_time=end_t,
                    lesson_type=ltype,
                    week_type=wtype
                )
            )
        return result

    async def fetch_teachers(self) -> List[str]:
        teachers = set()
        for item in self.RAW_LESSONS:
            if item[3]:
                teachers.add(item[3])
        return sorted(list(teachers))

    async def fetch_rooms(self) -> List[str]:
        rooms = set()
        for item in self.RAW_LESSONS:
            if item[5]:
                rooms.add(item[5])
        return sorted(list(rooms))
