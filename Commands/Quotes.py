import discord
from typing import Optional

from interaction_type import QuoteBotInteraction

from helpers.TimezoneHelpers import format_AEST
from helpers.UtilityHelpers import safe_send
from helpers.QuoteHelpers import *

async def run_repeat(interaction: QuoteBotInteraction, string: str):
  """
  Repeats the string specified by the user.

  Used to debug and check that the bot actually connected and responded to the user. 

  Essentially useless command.
  
  Returns:
    string that the user inputted
  """
  await safe_send(interaction, f'{string}')

async def run_rand_message(interaction: QuoteBotInteraction, user: discord.Member, limit: Optional[int], min_count: Optional[int]):
  """
  Sends a random single text user sent in this server.

  Quotes the user.
  Args:
    user: the user to quote. The bot will get a random message from this user.
    limit: the bot will go through the last n messages defined by this variable.
      
      ie. `limit` = 200, the bot will check the last 200 messages sent in this channel. Primarily here for timeout purposes. Defaulted to 200.
    min_count: the minimum number of messages sent by the user where the bot will not output a random message.
    
      ie. `min_count` = 2, if the user has sent < than 2, then the bot will not try to quote. This is mostly to reduce the possibility of the same messages being quoted over and over.
  
  Returns:
    The random message chosen:
    if `min_count` specified and num messages < `min_count`, an appropriate message.
  """
  # Don't try to quote itself
  if not interaction.client.user:
    print(f"Quotes/rand: interaction.client.user is None: interaction: {interaction}")
    return await safe_send(interaction, "An error occurred. Check logs for more info.")
  if user.id == interaction.client.user.id:
    return await safe_send(interaction, "Stop trying to quote me, I'm above your whimsical interactions!")

  if not limit:
    limit = 200
  if not min_count:
    min_count = 0

  msg = await _get_random_message(interaction, user, limit, min_count)
  
  if not msg:
    print(f"No messages sent: {limit}")
    return await safe_send(interaction, f"This user has not sent any messages in the last {limit} messages, disappointing...")

  timestamp = format_AEST(msg.created_at, "%Y-%m-%d %H:%M:%S")
  return await safe_send(interaction, '"' + msg.content + '"' + " - " + user.name + " (" + timestamp + ")")

async def _get_random_message(interaction: QuoteBotInteraction, user: discord.Member, limit: Optional[int], min_count: int):
  """
  Pseudo-random message.

  Returns:
    None if no messages found, message dict otherwise.
  """
  channel = interaction.channel
  # Get last n messages if user sent it
  messages = await get_last_n_messages(channel, limit, user) # type: ignore
  if not messages:
    return None

  return choose_random_message(messages, min_count)

