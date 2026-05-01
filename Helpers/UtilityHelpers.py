import asyncio
import discord
import time
from functools import wraps
from typing import Callable, Awaitable, TypeVar, Optional, Any
from typing_extensions import ParamSpec

from interaction_type import QuoteBotInteraction
from exceptions.quote_bot_errors import QuoteBotError
from exceptions.voice import UserNotInVcError
from exceptions.utils import TimeoutError

P = ParamSpec("P")
R = TypeVar("R")

async def safe_send(
  interaction: QuoteBotInteraction,
  message: Optional[str] = None,
  embeds: Optional[discord.Embed] = None,
  view: Optional[discord.ui.View] = None,
  file: Optional[discord.File] = None,
  ephemeral: bool = False
) -> discord.Message:
  """
  Sends bot response depending on whether or not interaction is deferred.

  Unified for all embeds, view, and files.

  Args:
    interaction: should always be given. The interaction that called this command.
    message: optional. The message to be sent.
    embed: optional. The embed to be sent.
    view: optional. The view to be sent.
    file: optional. The file to be sent.
    ephemeral: whether or not the message is only seen by the user who called the command.

  Returns:
    msg: the message the interaction sent.
  """
  kwargs: dict[Any, Any] = {"ephemeral": ephemeral}
  if message:
    kwargs["content"] = message
  if embeds:
    kwargs["embeds"] = [embeds]
  if view:
    kwargs["view"] = view
  if file:
    kwargs["file"] = file
  
  if interaction.response.is_done():
    return await interaction.followup.send(**kwargs, wait=True)
  else:
    await interaction.response.send_message(**kwargs)
    return await interaction.original_response()

async def safe_edit(
  interaction: QuoteBotInteraction,
  message: Optional[str] = None,
  embed: Optional[discord.Embed] = None,
  view: Optional[discord.ui.View] = None,
  message_id: Optional[int] = None
):
  """
  Edits original response.

  May also edit buttons on views.

  This is used inside button callbacks to refresh the message in-place.

  Edits based on deference.

  Note: followup.edit_message needs a message_id. Pass if possible, otherwise this will just use the original interaction's response.
  """
  kwargs: dict[Any, Any] = {}
  if embed:
    kwargs["embeds"] = [embed]
  if view:
    kwargs["view"] = view
  if message:
    kwargs["content"] = message
  
  if not message_id:
    if interaction.response.is_done():
      return await interaction.edit_original_response(**kwargs)
    else:
      return await interaction.response.edit_message(**kwargs)
  else:
    await interaction.followup.edit_message(message_id=message_id, **kwargs)

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
      except asyncio.TimeoutError:
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
