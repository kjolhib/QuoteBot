import asyncio
import discord
import time
from functools import wraps
from typing import Callable, Awaitable, TypeVar
from typing_extensions import ParamSpec

from interaction_type import QuoteBotInteraction
from exceptions.quote_bot_errors import QuoteBotError
from exceptions.voice import UserNotInVcError
from exceptions.utils import TimeoutError

P = ParamSpec("P")
R = TypeVar("R")

async def safe_send(interaction: discord.Interaction, message: str, ephemeral: bool=False) -> None:
  """
  Sends bot response depending on whether or not interaction is deferred
  """
  if interaction.response.is_done():
    await interaction.followup.send(message, ephemeral=ephemeral)
  else:
    await interaction.response.send_message(message, ephemeral=ephemeral)

async def safe_send_embed(interaction: discord.Interaction, embeds: discord.Embed) -> None:
  """
  Sends embed depending on deference
  """
  if interaction.response.is_done():
    await interaction.followup.send(embeds=[embeds])
  else:
    await interaction.response.send_message(embeds=[embeds])

async def safe_send_file(interaction: discord.Interaction, file: discord.File):
  """
  Sends a file depending on deference
  """
  if interaction.response.is_done():
    await interaction.followup.send(file=file)
  else:
    await interaction.response.send_message(file=file)

async def timeout_err(interaction: discord.Interaction):
  """
  Timeout error version of safe_send. 
  """
  if interaction.response.is_done():
    await interaction.followup.send("Command timed out. Try again later.")
  else:
    await interaction.response.send_message("Command timed out. Try again later.")

"""
Timeout factory
"""
def with_timeout(timeout: float = 7.0):
  """
  Factory decorator to wrap a command with timeout handler.

  Default timeout is 7.
  """
  def decorator(func: Callable[P, Awaitable[None]]):
    @wraps(func)
    async def wrapper(interaction: QuoteBotInteraction, *args: P.args, **kwargs: P.kwargs) -> None:
      start = time.perf_counter()
      try: 
        # defer response if needed
        if not interaction.response.is_done():
          await interaction.response.defer()
        
        # run original commadn with timeout
        await asyncio.wait_for(func(interaction, *args, **kwargs), timeout=timeout) # type: ignore
      except TimeoutError:
        raise TimeoutError(f"Command {func.__name__} timed out.", func.__name__, "")
      except QuoteBotError:
        raise
      finally:
        end = time.perf_counter()
        print(f"[{(func.__name__).upper()}] executed in {end-start:.3f}s")
    return wrapper # type: ignore
  return decorator

def bot_require_voice_client(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
  """
  Require voice factory.

  Functools is used to preserve discord.py's / command's ability to recognize the original function's signature for parsing arguments.
  
  Checks if a user is in vc.
  """
  @wraps(func)
  async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
    interaction: QuoteBotInteraction = args[0] # type: ignore
    state = interaction.client.get_guild_state(str(interaction.guild_id))
    if not state.voice_client:
      raise UserNotInVcError(f"You must be in a voice client to use this command.")
    return await func(*args, **kwargs) # type: ignore
  return wrapper
