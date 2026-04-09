import re
from string import capwords
from datetime import datetime
from zoneinfo import ZoneInfo

# Helper for timezone related features
def convert_to_AEST(utc_dt: datetime) -> datetime:
    """
    Converts a UTC datetime to Australia/Sydney timezone.
    Input: timezone-aware or naive UTC datetime.
    Output: timezone-aware datetime in AEST/AEDT.
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

def get_current_date(time_str, date_str, origin_country, origin_city):
  """
  Gets the origin time and date.
  """
  try:
     # Get zone info object
    zone = ZoneInfo(f"{origin_country}/{origin_city}")

    # get time
    time_pattern = r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    if not re.match(time_pattern, time_str):
      # not in HH:MM format
      return (402, "Please input time in the format HH:MM")

    hour = int(re.search(r"^([01]?[0-9]|2[0-3]):", time_str).group().strip(":"))
    mins = int(re.search(r":[0-5][0-9]$", time_str).group().strip(":"))

    # get date
    if date_str:
      # date specified
      pattern = r'\d{2}/\d{2}/\d{4}'
      if not re.match(pattern, date_str):
        # check date is in format DD/MM/YYYY
        return (401, "Please input date in the format DD/MM/YYYY")
      day, month, year = map(int, date_str.split("/"))
      dt_current_time = datetime(year, month, day,
                                hour, mins, 0, tzinfo=zone)
    else:
      # use current system date
      now = datetime.now()
      dt_current_time = datetime(now.year, now.month, now.day,
                                now.hour, now.minute, now.second, tzinfo=zone)
    
    return dt_current_time
  except Exception as e:
    print(f"[ERROR]: get_current_date: {e}")
    return (400, "Incorrect format.")

def convert_time(
    time_str: str,
    origin_country: str,
    origin_city: str,
    target_country: str,
    target_city: str,
    date_str: str | None = None
):
  """
  Converts a time from a given time, origin country/city, target country/city to another time
  """
  origin_country = capwords(origin_country).replace(" ", "_")
  origin_city = capwords(origin_city).replace(" ", "_")
  target_country = capwords(target_country).replace(" ", "_")
  target_city = capwords(target_city).replace(" ", "_")

  print(
f"""
Found data after formatting:
Origin: {origin_city}, {origin_country}
Target: {origin_city}, {origin_country}
"""
  )

  dt_origin = get_current_date(time_str, date_str, origin_country, origin_city)
  if not isinstance(dt_origin, datetime):
    # returned an error
    return dt_origin

  print(f"Received current date: {dt_origin.day}/{dt_origin.month}/{dt_origin.year} [{dt_origin.hour}:{dt_origin.minute}].")
  try:
    target_zone = ZoneInfo(f"{target_country}/{target_city}")
    dt_target = dt_origin.astimezone(target_zone)
  except Exception as e:
    print(f"Error converting origin to target: {e}")
    return (403, 403)
  
  return dt_origin, dt_target