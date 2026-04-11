import asyncio
import discord
import time
from functools import wraps
from typing import Callable, Awaitable
from typing_extensions import ParamSpec
from ErrorHandler import ErrorHandler

P = ParamSpec("P")

# General helpers
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
  TODO: Refactor using safe_send
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
  Factory decorator to wrap a command with timeout handler
  """
  def decorator(func: Callable[P, Awaitable[None]]):
    @wraps(func)
    async def wrapper(interaction: discord.Interaction, *args: P.args, **kwargs: P.kwargs) -> None:
      start = time.perf_counter()
      try: 
        # defer response if needed
        if not interaction.response.is_done():
          await interaction.response.defer()
        
        # run original commadn with timeout
        await asyncio.wait_for(func(interaction, *args, **kwargs), timeout=timeout) # type: ignore
      except asyncio.TimeoutError:
        await timeout_err(interaction)
      except Exception:
        # catch everything else
        ErrorHandler.report_exception(func.__name__)
        await safe_send(interaction, f"Something (my code) went wrong... is it a lingering response?")
      finally:
        end = time.perf_counter()
        print(f"[{(func.__name__).upper()}] executed in {end-start:.3f}s")
    return wrapper # type: ignore
  return decorator

# def display_table(interaction, header, body):
#   """
#   Using table2ascii library.
#   Given:
#   - header: [h1, h2, ...]
#   - body: [
#             [b1, b2, ...],
#             [b1, b2, ...],
#             ...
#           ]
#   Return a table
#   """
#   return t2a(header=header, body=body, style=PresetStyle.thin_compact)
