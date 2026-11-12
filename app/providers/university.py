from typing import List, Dict, Any, Optional
from app.providers.base import TimetableProvider, LessonDTO
from app.core.logging import logger


class UniversityAPIProvider(TimetableProvider):
    """
    Real university integration provider stub.
    Connect here with TSUE's HEMIS API, aSc Timetables API or website parser.
    """

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = api_url or "https://hemis.tsue.uz/rest/v1"
        self.api_key = api_key

    async def fetch_groups(self) -> List[Dict[str, Any]]:
        # TODO: Implement real HTTP request to university HEMIS/aSc API:
        # async with aiohttp.ClientSession() as session:
        #     headers = {"Authorization": f"Bearer {self.api_key}"}
        #     async with session.get(f"{self.api_url}/education/groups", headers=headers) as resp:
        #         return await resp.json()
        logger.info("UniversityAPIProvider.fetch_groups called (stub). Falling back to empty or seeded.")
        return []

    async def fetch_lessons(self, group_name: Optional[str] = None) -> List[LessonDTO]:
        # TODO: Implement real HTTP request to fetch lessons for group:
        # async with aiohttp.ClientSession() as session:
        #     url = f"{self.api_url}/education/schedule?group={group_name}"
        #     async with session.get(url) as resp:
        #         data = await resp.json()
        #         return [self._parse_lesson(item) for item in data]
        logger.info(f"UniversityAPIProvider.fetch_lessons called for {group_name} (stub).")
        return []

    async def fetch_teachers(self) -> List[str]:
        # TODO: Implement teacher list fetch from HEMIS
        return []

    async def fetch_rooms(self) -> List[str]:
        # TODO: Implement room list fetch from HEMIS
        return []
