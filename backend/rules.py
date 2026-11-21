from datetime import datetime, timedelta

CANCEL_WINDOW = timedelta(hours=2)


def can_cancel(slot_start: datetime, now: datetime | None = None) -> bool:
    """R6.2, R6.4, R6.5: cancellation allowed if the slot is at least
    2 hours away (exactly 2 hours is allowed)."""
    now = now or datetime.now()
    return slot_start - now >= CANCEL_WINDOW