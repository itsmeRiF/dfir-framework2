from datetime import datetime, timezone, timedelta


# India Standard Time
IST = timezone(timedelta(hours=5, minutes=30))


def now_ist():
    """
    Current time in IST
    """
    return datetime.now(IST)


def to_ist(dt):
    """
    Convert UTC datetime to IST
    """

    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(IST)


def format_ist(dt):
    """
    Format datetime for UI
    """

    if not dt:
        return "-"

    return to_ist(dt).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def ist_day_start_as_utc(dt=None):
    """
    Convert given IST datetime/date to UTC midnight.
    If no argument supplied, use current IST date.
    """

    if dt is None:
        dt = now_ist()

    # if only date object
    if not isinstance(dt, datetime):
        dt = datetime.combine(
            dt,
            datetime.min.time()
        )
        dt = dt.replace(tzinfo=IST)

    else:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IST)

        dt = dt.astimezone(IST)

        dt = dt.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    return dt.astimezone(timezone.utc)