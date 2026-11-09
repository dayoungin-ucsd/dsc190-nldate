from datetime import date

import pytest

from nldate import parse


def test_today():
    assert parse("today", date(2025, 11, 10)) == date(2025, 11, 10)


def test_tomorrow():
    assert parse("tomorrow", date(2025, 11, 10)) == date(2025, 11, 11)


def test_yesterday():
    assert parse("yesterday", date(2025, 11, 10)) == date(2025, 11, 9)


def test_in_five_days():
    assert parse("in 5 days", date(2025, 11, 10)) == date(2025, 11, 15)


def test_three_days_ago():
    assert parse("3 days ago", date(2025, 11, 10)) == date(2025, 11, 7)


def test_next_tuesday():
    assert parse("next Tuesday", date(2025, 11, 10)) == date(2025, 11, 11)


def test_last_friday():
    assert parse("last Friday", date(2025, 11, 10)) == date(2025, 11, 7)


def test_specific_date():
    assert parse("December 1, 2025") == date(2025, 12, 1)


def test_iso_date():
    assert parse("2025-12-01") == date(2025, 12, 1)


def test_days_before_date():
    assert parse("5 days before December 1st, 2025") == date(2025, 11, 26)


def test_weeks_after_tomorrow():
    assert parse("2 weeks after tomorrow", date(2025, 11, 10)) == date(2025, 11, 25)


def test_empty_string():
    with pytest.raises(ValueError):
        parse("")


def test_invalid_string():
    with pytest.raises(ValueError):
        parse("hello world")


def test_two_weeks_from_tomorrow():
    assert parse(
        "two weeks from tomorrow",
        date(2025, 11, 10),
    ) == date(2025, 11, 25)


def test_next_week():
    assert parse(
        "next week",
        date(2025, 11, 10),
    ) == date(2025, 11, 17)


def test_last_month():
    assert parse(
        "last month",
        date(2025, 11, 10),
    ) == date(2025, 10, 10)


def test_three_months_ago():
    assert parse(
        "3 months ago",
        date(2025, 11, 10),
    ) == date(2025, 8, 10)


def test_two_days_after_next_friday():
    assert parse(
        "2 days after next Friday",
        date(2025, 11, 10),
    ) == date(2025, 11, 16)
