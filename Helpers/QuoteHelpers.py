import discord
from typing import List, Optional
from random import randint

from exceptions.utils.lt_min_count_error import LTMinCountError

# Helpers for Quote.py
def choose_random_message(messages: List[discord.Message], min_count: int):
  """
  Choose a random message
  Args:
    messages: list of messages
    min_count: if the messages found are < this number, don't try to pick a random one
  Returns:
    message dict if found
    None if no messages
  Raises:
    LTMinCountError: if the user sent messages < `min_count`.
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
        print(f"[choose_random_message]: Too few messages sent by user, contents are as follows: \n{msg.content}")
        raise LTMinCountError("Too few messages sent by user.")
      return msg

async def get_last_n_messages(channel: discord.abc.Messageable, limit: Optional[int], user: discord.Member):
  """
  Returns:
    List of messages sent by user.
  """
  return [
    msg async for msg in channel.history(limit=limit) 
    if msg.author.id == user.id
  ]

