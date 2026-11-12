import asyncio
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from app.core.config import settings
from app.core.models import Lesson
from app.core.logging import logger

# Font definitions
FONT_REGULAR_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# Subject color map matching TSUE aSc Timetable
SUBJECT_COLOR_MAP: Dict[str, Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = {
    # Key: (Cell Background RGB, Room Tag Background RGB)
    "O'zbekistonning eng yangi tarixi_Ma": ((168, 172, 235), (218, 220, 245)),
    "O'zbekistonning eng yangi tarixi_Sem": ((122, 220, 150), (215, 218, 135)),
    "Dinshunoslik_Ma": ((145, 236, 230), (245, 215, 170)),
    "Dinshunoslik_Sem": ((255, 255, 210), (215, 218, 135)),
    "Iqtisodiyot nazariyasi_Ma": ((255, 248, 160), (215, 205, 120)),
    "Iqtisodiyot nazariyasi_Sem": ((145, 170, 225), (215, 218, 135)),
    "Amaliy matematika 1_Ma": ((255, 230, 170), (215, 218, 135)),
    "Amaliy matematika 1_Sem": ((255, 245, 170), (215, 218, 135)),
    "Kelajak soati Moliya 1-kurs": ((235, 135, 130), (240, 185, 230)),
    "Rus tili": ((215, 225, 255), (215, 218, 135)),
    "Falsafa_Ma": ((140, 235, 140), (215, 218, 135)),
    "Falsafa_Sem": ((215, 155, 155), (215, 218, 135)),
    "Jismoniy madaniyat va Sport": ((255, 255, 255), (215, 218, 135)),
}

DEFAULT_CELL_COLOR = ((235, 240, 250), (220, 225, 235))

SLOT_HEADERS = [
    (1, "8:00 - 9:20"),
    (2, "9:30 - 10:50"),
    (3, "11:00 - 12:20"),
    (4, "13:00 - 14:20"),
    (5, "14:30 - 15:50"),
    (6, "16:00 - 17:20"),
    (7, "17:30 - 18:50"),
    (8, "19:00 - 20:20"),
]

WEEKDAY_LABELS = [
    (1, "Mn"),
    (2, "Tu"),
    (3, "Wed"),
    (4, "Thu"),
    (5, "Fri"),
    (6, "Sat"),
]


def _get_subject_colors(subject_name: str, lesson_type: str) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """Determine cell color based on subject name and lesson type."""
    key = f"{subject_name}_{lesson_type}"
    if key in SUBJECT_COLOR_MAP:
        return SUBJECT_COLOR_MAP[key]
    for k, v in SUBJECT_COLOR_MAP.items():
        if k in subject_name:
            return v
    # Deterministic pastel color based on subject hash
    h = int(hashlib.md5(subject_name.encode()).hexdigest(), 16)
    r = 200 + (h % 50)
    g = 200 + ((h >> 4) % 50)
    b = 200 + ((h >> 8) % 50)
    return ((r, g, b), (220, 220, 160))


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    """Break text into lines that fit within max_width."""
    words = text.split()
    if not words:
        return []
    lines: List[str] = []
    current_line = words[0]
    for word in words[1:]:
        test_line = f"{current_line} {word}"
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines


def render_timetable_sync(
    group_name: str,
    lessons_by_day: Dict[int, List[Lesson]],
    week_type: str,
    semester_dates: str = "07/09/2026-30/10/2026"
) -> str:
    """
    Render timetable PNG synchronously and save to cache.
    Returns the file path.
    """
    # Create unique hash for cache
    data_str = f"{group_name}:{week_type}"
    for day in range(1, 7):
        for l in lessons_by_day.get(day, []):
            data_str += f":{day}-{l.slot_number}-{l.subject.name}-{l.lesson_type}-{l.teacher.full_name if l.teacher else ''}-{l.room.code if l.room else ''}"
    
    data_hash = hashlib.md5(data_str.encode()).hexdigest()
    safe_group_name = group_name.replace("/", "_").replace("\\", "_")
    output_path = os.path.join(settings.CACHE_DIR, f"{safe_group_name}_{week_type}_{data_hash}.png")

    if os.path.exists(output_path):
        return output_path

    # Dimensions
    WIDTH = 1360
    HEIGHT = 900
    HEADER_HEIGHT = 100
    FOOTER_HEIGHT = 45
    GRID_TOP = HEADER_HEIGHT + 10
    GRID_BOTTOM = HEIGHT - FOOTER_HEIGHT
    GRID_LEFT = 40
    GRID_RIGHT = WIDTH - 40

    DAY_COL_WIDTH = 55
    TOTAL_SLOTS = 8
    SLOT_WIDTH = (GRID_RIGHT - GRID_LEFT - DAY_COL_WIDTH) // TOTAL_SLOTS
    # Adjust right margin
    GRID_RIGHT = GRID_LEFT + DAY_COL_WIDTH + (SLOT_WIDTH * TOTAL_SLOTS)

    ROW_HEADER_HEIGHT = 68
    NUM_DAYS = 6
    DAY_ROW_HEIGHT = (GRID_BOTTOM - GRID_TOP - ROW_HEADER_HEIGHT) // NUM_DAYS
    GRID_BOTTOM = GRID_TOP + ROW_HEADER_HEIGHT + (DAY_ROW_HEIGHT * NUM_DAYS)

    image = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Load fonts
    font_title = get_font(FONT_BOLD_PATH, 34)
    font_subtitle = get_font(FONT_REGULAR_PATH, 15)
    font_slot_num = get_font(FONT_BOLD_PATH, 20)
    font_slot_time = get_font(FONT_REGULAR_PATH, 13)
    font_day = get_font(FONT_BOLD_PATH, 22)
    font_teacher = get_font(FONT_BOLD_PATH, 11)
    font_subj = get_font(FONT_BOLD_PATH, 11)
    font_room = get_font(FONT_BOLD_PATH, 11)
    font_footer = get_font(FONT_REGULAR_PATH, 13)

    # 1. Header: Draw University Logo if exists
    logo_path = "data/tsue_logo.png"
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path)
            logo = logo.resize((65, 88), Image.Resampling.LANCZOS)
            image.paste(logo, (GRID_LEFT + 5, 8))
        except Exception as e:
            logger.warning(f"Failed to paste logo: {e}")

    # Header Texts
    center_x = WIDTH // 2
    draw.text((center_x, 26), group_name, fill=(0, 0, 0), font=font_title, anchor="mt")
    subtitle_text = "Tashkent State University of Economics, O'zbekiston shoh ko'chasi 49"
    draw.text((center_x, 68), subtitle_text, fill=(30, 30, 30), font=font_subtitle, anchor="mt")

    # 2. Main Grid Outer Border
    BORDER_COLOR = (40, 40, 40)
    BORDER_WIDTH = 2
    draw.rectangle(
        [(GRID_LEFT, GRID_TOP), (GRID_RIGHT, GRID_BOTTOM)],
        outline=BORDER_COLOR,
        width=BORDER_WIDTH
    )

    # 3. Horizontal Grid Header Line
    draw.line(
        [(GRID_LEFT, GRID_TOP + ROW_HEADER_HEIGHT), (GRID_RIGHT, GRID_TOP + ROW_HEADER_HEIGHT)],
        fill=BORDER_COLOR,
        width=BORDER_WIDTH
    )

    # 4. Vertical line after day column
    day_line_x = GRID_LEFT + DAY_COL_WIDTH
    draw.line(
        [(day_line_x, GRID_TOP), (day_line_x, GRID_BOTTOM)],
        fill=BORDER_COLOR,
        width=BORDER_WIDTH
    )

    # 5. Slot Columns headers & vertical lines
    for i in range(TOTAL_SLOTS):
        col_x1 = day_line_x + i * SLOT_WIDTH
        col_x2 = col_x1 + SLOT_WIDTH
        
        # Vertical divider line
        if i > 0:
            draw.line([(col_x1, GRID_TOP), (col_x1, GRID_BOTTOM)], fill=(180, 180, 180), width=1)

        slot_num, slot_time = SLOT_HEADERS[i]
        slot_center_x = col_x1 + SLOT_WIDTH // 2
        draw.text((slot_center_x, GRID_TOP + 12), str(slot_num), fill=(0, 0, 0), font=font_slot_num, anchor="mt")
        draw.text((slot_center_x, GRID_TOP + 38), slot_time, fill=(30, 30, 30), font=font_slot_time, anchor="mt")

    # 6. Days rows & horizontal lines
    for idx, (weekday_num, day_str) in enumerate(WEEKDAY_LABELS):
        row_y1 = GRID_TOP + ROW_HEADER_HEIGHT + idx * DAY_ROW_HEIGHT
        row_y2 = row_y1 + DAY_ROW_HEIGHT
        
        if idx > 0:
            draw.line([(GRID_LEFT, row_y1), (GRID_RIGHT, row_y1)], fill=(180, 180, 180), width=1)

        # Day label centered
        draw.text(
            (GRID_LEFT + DAY_COL_WIDTH // 2, row_y1 + DAY_ROW_HEIGHT // 2),
            day_str,
            fill=(0, 0, 0),
            font=font_day,
            anchor="mm"
        )

        # Draw lessons for this day
        day_lessons = lessons_by_day.get(weekday_num, [])
        for lesson in day_lessons:
            slot_idx = lesson.slot_number - 1
            if slot_idx < 0 or slot_idx >= TOTAL_SLOTS:
                continue

            cell_x1 = day_line_x + slot_idx * SLOT_WIDTH + 1
            cell_x2 = cell_x1 + SLOT_WIDTH - 2
            cell_y1 = row_y1 + 1
            cell_y2 = row_y2 - 1

            cell_bg, room_bg = _get_subject_colors(lesson.subject.name, lesson.lesson_type)

            # Special case for Friday Sport spanning or single cell
            is_sport = "Sport" in lesson.lesson_type or "Jismoniy" in lesson.subject.name
            if is_sport:
                # Sport often takes 2 slots or has special banner
                cell_x2 = cell_x1 + (SLOT_WIDTH * 2) - 2

            # Draw cell background
            draw.rectangle([(cell_x1, cell_y1), (cell_x2, cell_y2)], fill=cell_bg)

            # Draw thin border around lesson
            draw.rectangle([(cell_x1, cell_y1), (cell_x2, cell_y2)], outline=(140, 140, 140), width=1)

            # Room bar at the bottom
            ROOM_BAR_HEIGHT = 20
            room_y1 = cell_y2 - ROOM_BAR_HEIGHT
            room_x1 = cell_x1 + 4
            room_x2 = cell_x2 - 4
            draw.rectangle([(room_x1, room_y1), (room_x2, cell_y2 - 2)], fill=room_bg)

            # Room code text
            room_text = lesson.room.code if lesson.room else ""
            draw.text((room_x2 - 4, room_y1 + 10), room_text, fill=(20, 20, 20), font=font_room, anchor="rm")

            # Teacher Name at top
            teacher_name = lesson.teacher.full_name if lesson.teacher else ""
            draw.text((cell_x1 + 6, cell_y1 + 4), teacher_name, fill=(0, 0, 0), font=font_teacher)

            # Subject Name and Type in middle (wrapped)
            full_subj_name = f"{lesson.subject.name} ({lesson.lesson_type})" if lesson.lesson_type else lesson.subject.name
            if is_sport:
                full_subj_name = f"{lesson.subject.name} ({lesson.room.code if lesson.room else ''})"

            max_txt_w = (cell_x2 - cell_x1) - 12
            subj_lines = _wrap_text(full_subj_name, font_subj, max_txt_w, draw)
            
            # Draw subject lines vertically centered
            start_sy = cell_y1 + 22
            for line in subj_lines[:3]:  # max 3 lines
                draw.text((cell_x1 + (cell_x2 - cell_x1)//2, start_sy), line, fill=(0, 0, 0), font=font_subj, anchor="mt")
                start_sy += 14

    # 7. Outer border re-affirm
    draw.rectangle(
        [(GRID_LEFT, GRID_TOP), (GRID_RIGHT, GRID_BOTTOM)],
        outline=BORDER_COLOR,
        width=BORDER_WIDTH
    )

    # 8. Footer
    footer_y = GRID_BOTTOM + 16
    draw.text(
        (GRID_LEFT, footer_y),
        f"Amal qilish muddati: {semester_dates}",
        fill=(50, 50, 50),
        font=font_footer
    )
    draw.text(
        (GRID_RIGHT, footer_y),
        "TSUE Telegram Bot | aSc Timetables",
        fill=(50, 50, 50),
        font=font_footer,
        anchor="ra"
    )

    image.save(output_path, "PNG", quality=95)
    logger.info(f"Timetable rendered and saved to {output_path}")
    return output_path


async def render_timetable_image(
    group_name: str,
    lessons_by_day: Dict[int, List[Lesson]],
    week_type: str,
    semester_dates: str = "07/09/2026-30/10/2026"
) -> str:
    """Async wrapper that renders the timetable in a thread executor."""
    return await asyncio.to_thread(
        render_timetable_sync,
        group_name,
        lessons_by_day,
        week_type,
        semester_dates
    )
