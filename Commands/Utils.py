from typing import Optional

from interaction_type import QuoteBotInteraction

# Helper imports
from helpers.utility_helpers import safe_send
from helpers.dice_helpers import compute_roll
from helpers.timezone_helpers import convert_time

async def run_d(interaction: QuoteBotInteraction, die_num: int, addon: Optional[int]=0):
  """
  Rolls a die with die_num faces and adds addon to the result.

  Returns:
    roll + addon
  """
  msg = compute_roll(die_num, addon)
  await safe_send(interaction, msg)

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
  dt_origin, dt_target = convert_time(
    time,
    origin_country,
    origin_city,
    target_country,
    target_city,
    date_str
  )

  await safe_send(interaction,
f"""
**Time Conversion:**
Origin: {origin_city}, {origin_country} [{dt_origin}]
Target: {target_city}, {target_country} [{dt_target}]
"""
                        )
