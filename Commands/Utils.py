import asyncio
import discord
import os
from typing import Optional

from interaction_type import QuoteBotInteraction

# Helper imports
from helpers.utility_helpers import safe_send, current_year
from helpers.secret_santa_helpers import read_secret_santa_data, secret_santa_data_to_embed
from helpers.dice_helpers import compute_roll
from helpers.timezone_helpers import convert_time
from helpers.secret_santa_helpers import (
  SANTA_EMOJIS, santa_lock, load_santa_file, save_santa_file,
  find_year_by_message, apply_reaction,
)

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

async def _add_santa_reaction(msg: discord.Message):
  for emoji in SANTA_EMOJIS:
    await msg.add_reaction(emoji)

async def run_secret_santa_info(interaction: QuoteBotInteraction, year: Optional[int] = None):
  """
  Command for listing information about a year's secret santa.
  """
  if year is None:
    year = current_year()
  if not os.path.exists(f"data/secret_santa/{year}.json"):
    await safe_send(interaction, f"No secret santa data found for year {year}. People weren't feeling it that year it seems.")
  async with santa_lock:
    print(f"Finding secret santa data for year: {year}")
    data = load_santa_file(year)
    msg= await safe_send(interaction, embeds=secret_santa_data_to_embed(data))
    data["message_id"] = msg.id
    save_santa_file(year, data)
  asyncio.create_task(_add_santa_reaction(msg))

async def process_secret_santa_reaction(client, payload: discord.RawReactionActionEvent):
  if client.user and payload.user_id == client.user.id:
    return

  emoji = str(payload.emoji)
  if emoji not in SANTA_EMOJIS or payload.member is None:
    return

  async with santa_lock:
    year = find_year_by_message(payload.message_id)
    if year is None:
      return
    data = load_santa_file(year)
    changed = apply_reaction(data, payload.member.display_name, emoji)
    if changed:
      save_santa_file(year, data)

  # retrieve and edit message
  msg = client.get_partial_messageable(payload.channel_id).get_partial_message(payload.message_id)
  if changed:
    await msg.edit(embeds=[secret_santa_data_to_embed(data)])
  try:
    await msg.remove_reaction(payload.emoji, payload.member)  # reset the "button"
  except discord.Forbidden:
    pass  # bot lacks management permissions; specifically i believe manager reactions