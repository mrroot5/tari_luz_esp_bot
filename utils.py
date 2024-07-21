import datetime
from typing import Optional


def since(dt=None, reference=datetime.datetime.now()) -> str:
    """Returns a textual description of time passed.

    Parameters:

     - dt: datetime is the date to calculate the difference from
           reference. If not used, take the value from the current
           datetime.

     - reference: datetime is the datetime used to get the difference
        ir delta. If not defined, default value is since the definition
        of the function, this is,since the moment the current run of the
        program started.
    """
    dt = dt or datetime.datetime.now()
    delta = dt - reference
    buff = []
    days = delta.days
    if days:
        buff.append(f"{days} {__pluralize(days, 'day')}")
    seconds = delta.seconds
    if seconds > 3600:
        hours = seconds // 3600
        buff.append(f"{hours} {__pluralize(hours, 'hour')}")
        seconds = seconds % 3600
    minutes = seconds // 60
    if minutes > 0:
        buff.append(f"{minutes} {__pluralize(minutes, 'minute')}")
    seconds = seconds % 60
    buff.append(f"{seconds} {__pluralize(seconds, 'second')}")
    return " ".join(buff)


def __pluralize(number: int, singular: str, plural: Optional[str] = None) -> str:
    if plural is None:
        plural = f"{singular}s"
    return singular if number == 1 else plural
