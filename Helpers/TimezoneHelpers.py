import re
from string import capwords
from datetime import datetime
from zoneinfo import ZoneInfo

from exceptions.timezone import time_format_error
from exceptions.timezone import date_format_error

# Helper for timezone related features
def convert_to_AEST(utc_dt: datetime) -> datetime:
    """
    Converts a UTC datetime to Australia/Sydney timezone.
    Args:
      utc_dt: timezone-aware or naive UTC datetime.
    Returns:
      timezone-aware datetime in AEST/AEDT.
    """
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=ZoneInfo("UTC"))
    return utc_dt.astimezone(ZoneInfo("Australia/Sydney"))

def format_AEST(utc_dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    """
    Converts UTC datetime to AEST and returns a formatted string.
    """
    local_dt = convert_to_AEST(utc_dt)
    return local_dt.strftime(fmt)

def get_current_date(time_str: str, date_str: str | None, origin_country: str, origin_city: str):
  """
  Gets the origin time and date.
  Args:
    date_str: the date in string format. If none, use current date.
    origin_country: the country to convert from.
    origin_city: the city to convert from.
  Raises:
    TimeFormatError: the time is not in the format HH:MM
    DateFormatError: date is not in the format DD/MM/YY
  """
    # Get zone info object
  zone = ZoneInfo(f"{origin_country}/{origin_city}")

  # get time
  time_pattern = r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
  if not re.match(time_pattern, time_str):
    # not in HH:MM format
    # return (402, "Please input time in the format HH:MM")
    raise time_format_error.TimeFormatError("Time is not in format HH:MM exactly.")

  hour = int(re.search(r"^([01]?[0-9]|2[0-3]):", time_str).group().strip(":")) # type: ignore
  mins = int(re.search(r":[0-5][0-9]$", time_str).group().strip(":")) # type: ignore

  # get date
  if date_str:
    # date specified
    pattern = r'\d{2}/\d{2}/\d{4}'
    if not re.match(pattern, date_str):
      # check date is in format DD/MM/YYYY
      # return (401, "Please input date in the format DD/MM/YYYY")
      raise date_format_error.DateFormatError("Date is not in the format DD/MM/YY. This ain't the freedom bird paradise of the U Ess of A")
    day, month, year = map(int, date_str.split("/"))
    dt_current_time = datetime(year, month, day,
                              hour, mins, 0, tzinfo=zone)
  else:
    # use current system date
    now = datetime.now()
    dt_current_time = datetime(now.year, now.month, now.day,
                              now.hour, now.minute, now.second, tzinfo=zone)
  
  return dt_current_time

def convert_time(
    time_str: str,
    origin_country: str,
    origin_city: str,
    target_country: str,
    target_city: str,
    date_str: str | None = None
):
  """
  Converts a time from a given time, origin country/city, target country/city to another time.
  Returns:
    The converted time in string format.
  """
  origin_country = capwords(origin_country).replace(" ", "_")
  origin_city = capwords(origin_city).replace(" ", "_")
  target_country = capwords(target_country).replace(" ", "_")
  target_city = capwords(target_city).replace(" ", "_")

  print(
f"""
[convert_time]:
Found data after formatting:
Origin: {origin_city}, {origin_country}
Target: {origin_city}, {origin_country}
"""
  )

  dt_origin = get_current_date(time_str, date_str, origin_country, origin_city)

  print(f"[convert_time]: Received current date: {dt_origin.day}/{dt_origin.month}/{dt_origin.year} [{dt_origin.hour}:{dt_origin.minute}].")
  target_zone = ZoneInfo(f"{target_country}/{target_city}")
  dt_target = dt_origin.astimezone(target_zone)
  
  return dt_origin, dt_target