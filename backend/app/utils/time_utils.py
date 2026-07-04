"""
Single source of truth for timestamps.

Previously the codebase mixed three different clocks across files:
  - models.py defaults        -> datetime.now(IST)         (aware, IST)
  - visitor_log_service.py    -> datetime.now()             (naive, server-local)
  - routes.py check-out       -> datetime.utcnow()           (naive, UTC)

Mixing aware and naive datetimes in the same column causes
`TypeError: can't subtract offset-naive and offset-aware datetimes`
the moment two rows created via different code paths are compared
(this is why search_visitor_logs had a `.replace(tzinfo=None)` patch).

Everywhere in the app should now import `now_ist` from here instead of
calling datetime.now() / datetime.utcnow() directly.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def now_ist() -> datetime:
    """Current time as a timezone-aware IST datetime."""
    return datetime.now(IST)
