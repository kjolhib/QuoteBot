from typing import Optional

from interaction_type import QuoteBotInteraction

# Helper imports
from exceptions.timezone import date_format_error
from helpers.UtilityHelpers import safe_send
from helpers.DiceHelpers import compute_roll
from exceptions.timezone import (time_format_error)
from exceptions.error_handler import report_error
from exceptions.dice import invalid_faces_error
from helpers.TimezoneHelpers import convert_time

async def run_d(interaction: QuoteBotInteraction, die_num: int, addon: Optional[int]=0):
  """
  Rolls a die with die_num faces and adds addon to the result.
  """
  try:
    msg = compute_roll(die_num, addon)
    await safe_send(interaction, msg)
  except invalid_faces_error.InvalidFacesError:
    await safe_send(interaction, f"I do not know what a D{die_num} is. Choose a die that has either 4 or 6 or more faces ya bingus.")
  except Exception as e:
    await safe_send(interaction, "Unknown error occurred. Check logs for more details.")
    report_error("run_d", e, f"attempted to roll a die with {die_num} faces, and {addon if addon else "no"} addons")

async def run_timezone_converter(
  interaction: QuoteBotInteraction,
  time: str,
  origin_country: str,
  origin_city: str, 
  target_country: str,
  target_city: str,
  date_str: str | None = None
):
  """
  Timezone converter
  """
  try:
    dt_origin, dt_target = convert_time(
      time,
      origin_country,
      origin_city,
      target_country,
      target_city,
      date_str
    )

    # No errors
    await safe_send(interaction,
f"""
**Time Conversion:**
Origin: {origin_city}, {origin_country} [{dt_origin}]
Target: {target_city}, {target_country} [{dt_target}]
"""
                          )
  except date_format_error:
    await safe_send(interaction, "Date must be in the format DD/MM/YYYY")
    print(f"[TIMEZONE]: incorrect date format.")
  except time_format_error:
    await safe_send(interaction, "Time must be in the format HH:MM")
    print(f"[TIMEZONE]: incorrect time format.")
  except Exception as e:
    await safe_send(interaction, 
f"""
Failed to convert:
[{time}], {date_str}, {origin_city}, {origin_country} to {target_city}, {target_country}
"""
                      )
    report_error("run_timezone_converter", e, 
                 f"""error converting timezone: {e}:
origin_country: {origin_country},
origin_city: {origin_city},
target_country: {target_country},
target_city: {target_city},
origin_date: {date_str}
"""
                 )
