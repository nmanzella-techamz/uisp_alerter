from datetime import datetime, timedelta
from textwrap import dedent
from math import floor
import re
from typing import Type

from dateutil import tz
from dateutil.zoneinfo import ZoneInfoFile, getzoneinfofile_stream


def get_human_readable_time(outage_ms: int):
    """From milliseconds, return human readable length of time."""
    times = (
        ("day", 86_400_000),
        ("hour", 3_600_000),
        ("minute", 60_000),
        ("second", 1_000),
    )
    for time_name, time_ms in times:
        if outage_ms >= time_ms:
            num = floor(outage_ms / time_ms)
            text = f"{num} {time_name}"
            if num > 1:
                return text + "s"
            return text
    return "1 second"


def get_ordinal_suffix(day: int) -> str:
    """
    Return the ordinal suffix for a given day of the month.
    :param day: Day of the month (1-31)
    :return: Ordinal suffix as a string
    """
    if 10 <= day % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return suffix


def human_readable_datetime(dt: datetime):
    day_start = dt.day
    ordinal_suffix_start = get_ordinal_suffix(day_start)
    hour = str(int(dt.strftime("%I")))
    am_pm = dt.strftime("%p").lower()
    return dt.strftime(
        f"%A, %B {day_start}{ordinal_suffix_start}, %Y at {hour}:%M{am_pm}"
    )


def timedelta_to_human_readable(td: timedelta) -> str:
    """Converts a timedelta object to a human-readable string."""
    days, remainder = divmod(td.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    result = []
    if days:
        result.append(f"{int(days)} day{'s' if days != 1 else ''}")
    if hours:
        result.append(f"{int(hours)} hour{'s' if hours != 1 else ''}")
    if minutes:
        result.append(f"{int(minutes)} minute{'s' if minutes != 1 else ''}")
    if seconds:
        result.append(f"{int(seconds)} second{'s' if seconds != 1 else ''}")
    return ", ".join(result)


def convert_seconds_to_milliseconds(num: int) -> int:
    return num * 1_000


def convert_milliseconds_to_seconds(num: int) -> int:
    return num // 1_000


def get_all_time_zone_names():
    return ZoneInfoFile(getzoneinfofile_stream()).zones.keys()


def get_datetime(timestamp: str, timezone: Type[tz.tzfile]) -> datetime:
    return datetime.fromisoformat(timestamp).astimezone(timezone)


def strip_leading_whitespace(text: str) -> str:
    return re.sub("\n +", "\n", text.strip())


def create_alert_message(outage: dict, timezone: Type[tz.tzfile]) -> str:
    start = human_readable_datetime(get_datetime(outage["startTimestamp"], timezone))
    if outage["endTimestamp"] is None:
        end = ""
    else:
        end = f"\nEnd: {human_readable_datetime(get_datetime(outage['endTimestamp'], timezone))}"
    message = f"""
    Alert for "{outage['device']['name']}" for {get_human_readable_time(outage["aggregatedTime"])}
    Issue Type: {outage['type'].title()}
    Issue is still active: {outage['inProgress']}
    Start: {start}{end}
    Model: {outage['device']['model']}
    MAC Address: {outage['device']['mac']}
    """
    return strip_leading_whitespace(message) + "\n"


def create_mail_subject(site_name: str, alert_number: int) -> str:
    return f"{alert_number} Alert{'s'[:alert_number^1]} for {site_name} UISP Devices"


def create_mail_body(
    site_name: str,
    timezone_name: str,
    start_datetime: datetime,
    end_datetime: datetime,
    alerts: list[str],
) -> str:
    total = len(alerts)
    body_start = dedent(f"""\
    {total} alert{'s'[:total^1]} from UISP devices at {site_name} from {human_readable_datetime(start_datetime)} to {human_readable_datetime(end_datetime)}.\n
    Times below are in the "{timezone_name}" timezone.\n
    """)
    body = body_start + "\n".join(alerts)
    return body


def get_datetime_now_with_minute_precision(timezone: Type[tz.tzfile]) -> datetime:
    now = datetime.now(timezone)
    return now.replace(second=0, microsecond=0)


def get_timezone(timezone_name: str) -> Type[tz.tzfile]:
    timezone: Type[tz.tzfile] = tz.gettz(timezone_name)
    if timezone is None:
        return ValueError("Timezone cannot be None")
    return timezone
