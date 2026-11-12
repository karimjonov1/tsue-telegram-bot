from datetime import date
from app.services.timetable import get_week_info, get_week_type_display


def test_week_a_b_alternating():
    # Semester starts Monday, 2026-09-07 (Week 1 -> Week A)
    w_type, w_num = get_week_info(date(2026, 9, 7))
    assert w_num == 1
    assert w_type == "WEEK_A"
    assert get_week_type_display(w_type) == "A-hafta (Toq)"

    # Wednesday of Week 1 is still Week A
    w_type, w_num = get_week_info(date(2026, 9, 9))
    assert w_num == 1
    assert w_type == "WEEK_A"

    # Monday of Week 2 (2026-09-14) is Week B
    w_type, w_num = get_week_info(date(2026, 9, 14))
    assert w_num == 2
    assert w_type == "WEEK_B"
    assert get_week_type_display(w_type) == "B-hafta (Juft)"

    # Monday of Week 3 (2026-09-21) is Week A again
    w_type, w_num = get_week_info(date(2026, 9, 21))
    assert w_num == 3
    assert w_type == "WEEK_A"

    # Monday of Week 4 (2026-09-28) is Week B
    w_type, w_num = get_week_info(date(2026, 9, 28))
    assert w_num == 4
    assert w_type == "WEEK_B"
