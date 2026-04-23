import os
import json
import random
from typing import TypedDict

from exceptions.dnd import weather_exists_error, weather_missing_error, weather_empty_error, negative_count_error

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
FILE_PATH = os.path.join(os.path.dirname(__file__), "../data/weather_probabilities.json")

class WeatherStats(TypedDict):
  """
  For statistics related to the weather json
  """ 
  total_rolls: int
  percentages: dict[str, float]
  most_common: str
  least_common: str

class WeatherData():
  """
  Contains data in JSON format: dict[str, int].
  Has a weighted random generator that generates a random weather, and statistics related to it.
  """
  def __init__(self, data: dict[str, int], fp: str=FILE_PATH):
    self._data: dict[str, int] = data
    self._fp = fp

  def get_data(self) -> dict[str, int]:
    """
    Gets the weather data as a dictionary.
    Returns:
      - dict[str, int]: the weather dictionary, map: scenario -> times rolled
    """
    return self._data

  def select_weighted_random(self) -> str:
    """
    Pseudo-weighted random generator.
    The more often the weather is chosen before (higher int value), the less often it gets chosen.
    Returns:
      - string: the weather that got chosen
    """
    if not self._data:
      raise weather_empty_error.WeatherEmptyError(f"[select_weighted_random]: Weather dictionary is empty.")
    total = sum(self._data.values())
    if total == 0:
      # empty
      return random.choice(list(self._data.keys()))
    
    weights: list[float] = []

    # Collect the information from the json, and weight each weather's probability by their counts.
    # More counts = less probability of being chosen.
    for _, count in self._data.items():
      weights.append(1/(count+1))
    return random.choices(list(self._data.keys()), weights=weights)[0]

  def statistics(self) -> WeatherStats:
    """
    Gets statistics related to the rolls.
    Returns:
      - Total rolls
      - Percentages
      - Most common weather
      - Least common weather
    """
    total = sum(self._data.values())
    if total == 0:
      return {
        "total_rolls": total,
        "percentages": {k: 0.0 for k in self._data},
        "most_common": "N/A",
        "least_common": "N/A"
      }
    return {
      "total_rolls": total,
      "percentages": {k: round(v / total * 100, 2) for k, v in self._data.items()},
      "most_common": max(self._data, key=lambda k: self._data[k]),
      "least_common": min(self._data, key=lambda k: self._data[k])
    }

  def increment_val(self, w: str) -> None:
    """
    Increments the int value of a weather.
    Ie. This weather has now been rolled another 1 time.
    """
    if w not in self._data:
      raise weather_missing_error.WeatherMissingError(f"[increment_val]: Weather {w} not found in weather data.")
    self._data[w] += 1

  def add_new_weather(self, w: str) -> None:
    """
    Adds a weather to the dict.
    Raises:
      - WeatherExistsError: if weather already exists
    """
    if w in self._data:
      raise weather_exists_error.WeatherExistsError(f"[add_new_weather]: Weather {w} already exists.")
    
    self._data[w] = 0

  def remove_weather(self, w: str) -> int:
    """
    Removes a specified weather.
    Raises:
      - WeatherMissingError: if weather does not exist
    Returns:
      - Counter: the int value related to the weather key before being removed
    """
    if w not in self._data:
      raise weather_missing_error.WeatherMissingError(f"[remove_weather]: Weather {w} missing from dictionary.")
    
    c = self._data[w]
    del self._data[w]
    return c

  def modify_weather(self, w: str, new_c: int) -> int:
    if w not in self._data:
      raise weather_missing_error.WeatherMissingError(f"[modify_weather]: Weather {w} does not exist in dictionary.")
    if new_c < 0:
      raise negative_count_error.NegativeCountError(f"You cannot modify count to a negative value.")
    old_c = self._data[w]
    self._data[w] = new_c
    return old_c

  def reset_data(self) -> None:
    """
    Resets the current ._data to the initial data.
    Mostly here for debugging.
    In reality, the discord api will interact directly with the file, with load/save_weather.
    """
    self._data = get_init_data().get_data()

def reset_json(fp: str=FILE_PATH) -> None:
  """
  Resets weather_probabilities.json to INIT_DATA.
  """
  save_weather(get_init_data(), fp)

def get_weather_path():
  """
  Gets the file name and path
  """
  return FILE_PATH

def get_init_data() -> WeatherData:
  """
  Returns the initial weather data
  """
  return WeatherData(INIT_DATA.copy()) # avoid mutating

def load_weather(fp: str=FILE_PATH):
  """
  Loads the weather JSON data in hash-map (dict) form, weather-number_rolled.
  If no file exists, re-creates it with initial data.
  Returns:
    - JSON object of the hash map
    - fp: optional. path to the .json file
  """
  if not os.path.exists(fp):
    with open(fp, "w") as f:
      json.dump(INIT_DATA, f, indent=4)
  
  with open(fp, "r") as f:
    return WeatherData(json.load(f))

def save_weather(wd: WeatherData, fp: str=FILE_PATH):
  """
  Saves the weather data into a file, if not specified, default to data/weather_probabilities.json.
  Params:
    - wd: the WeatherData object to be saved
    - fp: optional. path to the .json file
  """
  with open(fp, "w") as f:
    json.dump(wd.get_data(), f, indent=4)
