import json
import os
from functools import wraps
from typing import Callable, Awaitable, TypeVar
from typing_extensions import ParamSpec

from interaction_type import QuoteBotInteraction

from helpers.UtilityHelpers import safe_send

P = ParamSpec("P")
R = TypeVar("R")

FILE_NAME = os.path.join(os.path.dirname(__file__), "../data/weather_probabilities.json")
INIT_DATA = {
      "Light Rain": 0,
      "Heavy Rain": 0,
      "Thunderstorm": 0,
      "Eclipse": 0,
      "Foggy": 0,
      "Cloudy": 0,
      "Sunny": 0,
      "Drought": 0,
      "Mana Storm": 0
    }

def load_weather():
  """
  Loads the weather JSON data in hash-map (dict) form, weather-number_rolled.
  Returns:
    - json object of the hash map
  """
  if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w") as f:
      json.dump(INIT_DATA, f, indent=4)
  with open(FILE_NAME, "r") as f:
    return json.load(f)

def save_weather(data: dict[str, int]):
  """
  Saves the weather data after session end.
  Params:
    - data: the dictionary data to be saved
  """
  with open(FILE_NAME, "w") as f:
    json.dump(data, f, indent=4)

def get_weather_path():
  """
  Gets the file name and path
  """
  return FILE_NAME

def get_init_data():
  """
  Returns the initial weather data
  """
  return INIT_DATA

def require_valid_session(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
  """
  Require session to be active.
  """
  @wraps(func)
  async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
    interaction: QuoteBotInteraction = args[0] # type: ignore
    state = interaction.client.get_guild_state(str(interaction.guild_id))
    if not state.dnd_session:
      func_name_msg_dict = {
        "run_end": "No session is active.",
        "run_scenario_die": "No session is active.",
        "run_list_dice": "No session is active.",
        "run_new_die_instance": "Please only create instance die during a DnD session.",
        "run_generate_weather": "Please only generate weathers during a DnD session."
      }
      msg = func_name_msg_dict.get(func.__name__, "No session is active.")
      await safe_send(interaction, msg)
      return #type: ignore
    return await func(*args, **kwargs) # type: ignore
  return wrapper
