from datetime import time
from unittest.mock import patch

import pandas as pd
import pytest
from exchange_calendars import get_calendar

from pylivetrader.executor import realtimeclock
from pylivetrader.executor.realtimeclock import (
    BAR, BEFORE_TRADING_START_BAR, SESSION_START, RealtimeClock,
)

BTS = (time(8, 45), 'America/New_York')


class _Stop(Exception):
    pass


class FakeWallClock:
    """Patches the clock's notion of "now" (UTC). Every sleep() call moves
    time forward by one minute so the clock can make progress."""

    def __init__(self, now, stop_on_sleep=False):
        self.now = pd.Timestamp(now, tz='UTC')
        self.sleeps = 0
        self.stop_on_sleep = stop_on_sleep

    def _to_datetime(self, arg, *args, **kwargs):
        if isinstance(arg, str) and arg == 'now':
            return self.now
        return self._real_to_datetime(arg, *args, **kwargs)

    def _sleep(self, seconds):
        self.sleeps += 1
        if self.stop_on_sleep:
            raise _Stop
        self.now += pd.Timedelta('1min')

    def __enter__(self):
        self._real_to_datetime = pd.to_datetime
        self._patches = [
            patch.object(pd, 'to_datetime', self._to_datetime),
            patch.object(realtimeclock, 'sleep', self._sleep),
        ]
        for p in self._patches:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in self._patches:
            p.stop()


def _clock():
    return RealtimeClock(get_calendar('NYSE'), BTS, minute_emission=False)


def test_realtime_clock_emits_events_during_session():
    # Monday 2026-11-16 10:00 ET, i.e. during the regular session.
    with FakeWallClock('2026-11-16 15:00'):
        events = []
        for event in _clock():
            events.append(event)
            if len(events) == 3:
                break

    (dt0, a0), (dt1, a1), (dt2, a2) = events
    assert a0 == SESSION_START
    # the session label handed to the algorithm stays a tz-aware UTC midnight
    assert dt0 == pd.Timestamp('2026-11-16', tz='UTC')
    assert str(dt0.tzinfo) == 'UTC'
    assert a1 == BEFORE_TRADING_START_BAR
    assert a2 == BAR
    assert dt2 == pd.Timestamp('2026-11-16 15:01', tz='UTC')


def test_realtime_clock_waits_on_non_session_day():
    # Saturday: not a session, so the clock must just sleep (and not raise
    # because of the timestamp it asks the calendar about).
    with FakeWallClock('2026-11-14 15:00', stop_on_sleep=True) as wall:
        with pytest.raises(_Stop):
            next(iter(_clock()))
    assert wall.sleeps == 1
