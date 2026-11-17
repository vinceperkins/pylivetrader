import pytest
from exchange_calendars import get_calendar

from pylivetrader.misc import events


@pytest.fixture(scope='module')
def cal():
    return get_calendar('NYSE')


def _fires(rule, cal, start, end):
    rule.cal = cal
    return [
        s.date().isoformat()
        for s in cal.sessions_in_range(start, end)
        if rule.should_trigger(cal.session_open(s))
    ]


def test_week_start_and_end_rules(cal):
    # Mondays / Fridays of 4 consecutive weeks (no holidays in them)
    assert _fires(events.NthTradingDayOfWeek(0), cal,
                  '2026-10-26', '2026-11-20') == [
        '2026-10-26', '2026-11-02', '2026-11-09', '2026-11-16']
    assert _fires(events.NDaysBeforeLastTradingDayOfWeek(0), cal,
                  '2026-10-26', '2026-11-20') == [
        '2026-10-30', '2026-11-06', '2026-11-13', '2026-11-20']


def test_week_rule_across_new_year(cal):
    # 2025-12-29..2026-01-02 is one ISO week; it must trigger exactly once,
    # and not be merged with the first week of January 2025.
    fired = _fires(events.NthTradingDayOfWeek(0), cal,
                   '2024-12-30', '2026-01-09')
    assert fired.count('2025-12-29') == 1
    assert '2025-12-30' not in fired and '2025-12-31' not in fired
    assert '2026-01-02' not in fired
    assert '2025-01-02' in fired or '2024-12-30' in fired


def test_month_start_and_end_rules(cal):
    assert _fires(events.NthTradingDayOfMonth(0), cal,
                  '2026-10-26', '2026-12-04') == ['2026-11-02', '2026-12-01']
    assert _fires(events.NDaysBeforeLastTradingDayOfMonth(0), cal,
                  '2026-10-26', '2026-12-04') == ['2026-10-30', '2026-11-30']


def test_not_half_day(cal):
    rule = events.NotHalfDay()
    rule.cal = cal
    assert not rule.should_trigger(cal.session_open('2026-11-27'))
    assert rule.should_trigger(cal.session_open('2026-11-25'))
