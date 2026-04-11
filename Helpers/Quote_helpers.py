import discord
from typing import List, Optional
from random import randint

# Helpers for Quote.py
def choose_random_message(messages: List[discord.Message], min_count: int):
  """
  Choose a random message
  Params:
    - messages: list of messages
    - min_count: if the messages found are < this number, don't try to pick a random one
  Returns:
    - message dict if found
    - None if no messages
    - 401 if messages < min_count
  """
  if not messages:
    return None
  
  start_index = randint(0, len(messages) - 1)
  # Scan forward from random start, wrap around
  for i in range(len(messages)):
    msg = messages[(start_index + i) % len(messages)]

    # ignore non empty, otherwise print debugs
    if (msg.content).strip() != "":
      print(f"[RAND] Found message, number of messages pooled: {len(messages)}")
      if len(messages) < min_count:
        # Too little messages sent
        print(f"Too few messages sent by user, contents are as follows: \n{msg.content}")
        return 401
      return msg

async def get_last_n_messages(channel: discord.abc.Messageable, limit: Optional[int], user: discord.Member):
  """
  Returns:
    - List of messages sent by user
  """
  return [
    msg async for msg in channel.history(limit=limit) 
    if msg.author.id == user.id
  ]

async def get_random_message(interaction: discord.Interaction, user: discord.Member, limit: Optional[int], min_count: int):
  """
  Pseudo-random message, discord wrapper
  """
  channel = interaction.channel
  # Get last n messages if user sent it
  messages = await get_last_n_messages(channel, limit, user) # type: ignore
  if not messages:
    return None

  return choose_random_message(messages, min_count)
