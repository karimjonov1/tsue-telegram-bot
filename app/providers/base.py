from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LessonDTO:
    group_name: str
    subject_name: str
    teacher_name: Optional[str]
    room_code: Optional[str]
    weekday: int  # 1..6
    slot_number: int  # 1..8
    start_time: str
    end_time: str
    lesson_type: str  # Ma, Sem, Lab, Sport
    week_type: str = "EVERY"  # EVERY, WEEK_A, WEEK_B


class TimetableProvider(ABC):
    """Abstract interface for university timetable providers."""

    @abstractmethod
    async def fetch_groups(self) -> List[Dict[str, Any]]:
        """Fetch list of groups (e.g. [{'name': 'MMT-950/26i', 'course': 1, 'faculty': 'Moliya'}])"""
        pass

    @abstractmethod
    async def fetch_lessons(self, group_name: Optional[str] = None) -> List[LessonDTO]:
        """Fetch lessons for a specific group or all groups."""
        pass

    @abstractmethod
    async def fetch_teachers(self) -> List[str]:
        """Fetch list of teacher names."""
        pass

    @abstractmethod
    async def fetch_rooms(self) -> List[str]:
        """Fetch list of room codes."""
        pass
