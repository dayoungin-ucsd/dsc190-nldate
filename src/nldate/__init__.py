"""
def main() -> None:
    print("Hello from nldate!")
"""

import calendar
import re
from datetime import date, timedelta

MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}
MONTHS.update({name.lower(): i for i, name in enumerate(calendar.month_abbr) if name})

WEEKDAYS = {name.lower(): i for i, name in enumerate(calendar.day_name)}
WEEKDAYS.update({name.lower(): i for i, name in enumerate(calendar.day_abbr)})

NUMBERS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}


def _number(s: str) -> int:
    s = s.strip().lower()
    if s in NUMBERS:
        return NUMBERS[s]
    return int(s)


def _add_months(d: date, months: int) -> date:
    total = d.year * 12 + d.month - 1 + months
    year, month_index = divmod(total, 12)
    month = month_index + 1

    if not 1 <= year <= 9999:
        raise ValueError("Date out of range")

    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _apply_offset(d: date, amount: int, unit: str) -> date:
    unit = unit.lower().rstrip("s")

    if unit == "day":
        return d + timedelta(days=amount)

    if unit == "week":
        return d + timedelta(weeks=amount)

    if unit == "month":
        return _add_months(d, amount)

    if unit == "year":
        return _add_months(d, amount * 12)

    raise ValueError(f"Unknown unit: {unit}")


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)

    if not s:
        raise ValueError("Empty date string")

    # Basic relative dates
    simple = {
        "today": 0,
        "tomorrow": 1,
        "yesterday": -1,
        "day after tomorrow": 2,
        "day before yesterday": -2,
    }

    if s in simple:
        return today + timedelta(days=simple[s])

    # ISO dates: 2025-12-01
    try:
        return date.fromisoformat(s)
    except ValueError:
        pass

    # Numeric dates: 12/01/2025
    match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if match:
        month, day, year = map(int, match.groups())
        return date(year, month, day)
    
    # Year-first dates: 2025/12/04
    match = re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", s)
    if match:
        year, month, day = map(int, match.groups())
        return date(year, month, day)

    # Month name dates: December 1st, 2025
    match = re.fullmatch(
        r"([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?"
        r",?\s*(\d{4})?",
        s,
    )

    if match:
        month_name, day_str, year_str = match.groups()

        if month_name in MONTHS:
            month = MONTHS[month_name]
            day = int(day_str)
            year = int(year_str) if year_str else today.year
            return date(year, month, day)

    # Day-first dates: 1 December 2025
    match = re.fullmatch(
        r"(\d{1,2})(?:st|nd|rd|th)?\s+"
        r"([a-z]+),?\s*(\d{4})?",
        s,
    )

    if match:
        day_str, month_name, year_str = match.groups()

        if month_name in MONTHS:
            day = int(day_str)
            month = MONTHS[month_name]
            year = int(year_str) if year_str else today.year
            return date(year, month, day)

    # Relative periods: next week, last month, this year
    match = re.fullmatch(
        r"(next|last|this)\s+(day|week|month|year)s?",
        s,
    )

    if match:
        direction, unit = match.groups()

        if direction == "next":
            amount = 1
        elif direction == "last":
            amount = -1
        else:
            amount = 0

        return _apply_offset(today, amount, unit)

    # Weekdays: next Tuesday, last Friday, this Monday
    match = re.fullmatch(r"(next|last|this)\s+([a-z]+)", s)

    if match:
        direction, weekday_name = match.groups()

        if weekday_name in WEEKDAYS:
            target = WEEKDAYS[weekday_name]
            current = today.weekday()

            if direction == "next":
                delta = (target - current) % 7
                if delta == 0:
                    delta = 7

            elif direction == "last":
                delta = -((current - target) % 7)
                if delta == 0:
                    delta = -7

            else:
                delta = target - current

            return today + timedelta(days=delta)

    # In 5 days / 3 weeks ago
    number_pattern = (
        r"(\d+|a|an|one|two|three|four|five|six|"
        r"seven|eight|nine|ten|eleven|twelve)"
    )
    unit_pattern = r"(days?|weeks?|months?|years?)"

    match = re.fullmatch(
        rf"in\s+{number_pattern}\s+{unit_pattern}",
        s,
    )

    if match:
        amount = _number(match.group(1))
        unit = match.group(2)
        return _apply_offset(today, amount, unit)

    match = re.fullmatch(
        rf"{number_pattern}\s+{unit_pattern}\s+ago",
        s,
    )

    if match:
        amount = _number(match.group(1))
        unit = match.group(2)
        return _apply_offset(today, -amount, unit)

    # 5 days from now / 2 weeks from today
    match = re.fullmatch(
        rf"{number_pattern}\s+{unit_pattern}"
        r"\s+from\s+(now|today)",
        s,
    )

    if match:
        amount = _number(match.group(1))
        unit = match.group(2)
        return _apply_offset(today, amount, unit)

    # 5 days before December 1st, 2025
    # 2 weeks after tomorrow
    match = re.fullmatch(
        rf"{number_pattern}\s+{unit_pattern}"
        r"\s+(before|after|from)\s+(.+)",
        s,
    )

    if match:
        amount = _number(match.group(1))
        unit = match.group(2)
        direction = match.group(3)
        reference = match.group(4)

        base = parse(reference, today)

        if direction == "before":
            amount = -amount

        return _apply_offset(base, amount, unit)

    # 1 year and 2 months after yesterday
    match = re.fullmatch(
        rf"{number_pattern}\s+{unit_pattern}"
        rf"\s+and\s+{number_pattern}\s+{unit_pattern}"
        r"\s+(before|after)\s+(.+)",
        s,
    )

    if match:
        amount1 = _number(match.group(1))
        unit1 = match.group(2)
        amount2 = _number(match.group(3))
        unit2 = match.group(4)
        direction = match.group(5)
        reference = match.group(6)

        base = parse(reference, today)

        sign = -1 if direction == "before" else 1

        base = _apply_offset(base, sign * amount1, unit1)
        base = _apply_offset(base, sign * amount2, unit2)

        return base

    raise ValueError(f"Unrecognized date expression: {s}")
