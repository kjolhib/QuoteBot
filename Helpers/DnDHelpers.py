from functools import wraps
from typing import Callable, Awaitable, TypeVar
from typing_extensions import ParamSpec

from interaction_type import QuoteBotInteraction

from exceptions.guild import null_session_error

P = ParamSpec("P")
R = TypeVar("R")

def require_valid_session(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
  """
  Require session to be active.

  Checks whether or not the given interaction's guild has a dnd session to be active.
  
  The following commands require it to be active:
    - /end: ends dnd session
    - /instance_die: rolls a scenario die
    - /new_die: creates a new instance die
    - /weather: generates a new weather

  Raises:
    NullSessionError: `dnd_session` was found to be null. This decorator requires it to be valid.
  """
  @wraps(func)
  async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
    interaction: QuoteBotInteraction = args[0] # type: ignore
    state = interaction.client.get_guild_state(str(interaction.guild_id))
    if not state.dnd_session:
      raise null_session_error.NullSessionError(f"You need to start a DnDSession to use this command.")
    return await func(*args, **kwargs) # type: ignore
  return wrapper
