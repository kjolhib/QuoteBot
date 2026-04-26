from functools import wraps
from typing import Callable, Awaitable, TypeVar
from typing_extensions import ParamSpec

from interaction_type import QuoteBotInteraction

from helpers.UtilityHelpers import safe_send

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
  """
  @wraps(func)
  async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
    interaction: QuoteBotInteraction = args[0] # type: ignore
    state = interaction.client.get_guild_state(str(interaction.guild_id))
    if not state.dnd_session:
      func_name_msg_dict = {
        "run_end": "No session is active.",
        "run_instance_die": "No session is active.",
        "run_list_dice": "No session is active.",
        "run_new_die": "Please only create instance die during a DnD session.",
        "run_generate_weather": "Please only generate weathers during a DnD session."
      }
      msg = func_name_msg_dict.get(func.__name__, "No session is active.")
      await safe_send(interaction, msg)
      return #type: ignore
    return await func(*args, **kwargs) # type: ignore
  return wrapper
