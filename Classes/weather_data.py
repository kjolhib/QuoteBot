import os
import json
import random
from dataclasses import dataclass
from discord.embeds import Embed as de
from discord.colour import Colour as dc

from exceptions.dnd import weather_exists_error, weather_missing_error, weather_empty_error, negative_count_error

INITDATA = {
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

@dataclass
class WeatherStats():
  """
  Custom class for typing statistics.
  """
  total_rolls: int
  percentages: dict[str, float]
  most_common: str
  least_common: str

  def to_embed(self) -> de:
    """
    Turns the attributes of this class into a discord embed.

    Returns:
      Embed: 
      
      Format:
        "Total Rolls": total_rolls
        "Percentages": {weather: percentage_rolled}
        "Most Common": most_common
        "Least Common": least_common
    """
    embed = de(title="Statistics regarding weather rolls.", colour=dc.blue())
    embed.add_field(name="Total Rolls", value=self.total_rolls)
    embed.add_field(name="Percentages", value="\n".join(f"{k}: {round(v, 2)}" for k, v in self.percentages.items()) or None)
    embed.add_field(name="Most Common", value=self.most_common)
    embed.add_field(name="Least Common", value=self.least_common)
    return embed

class WeatherData():
  """
  Contains data in JSON format: dict[str, int].

  Has a weighted random generator that generates a random weather, and statistics related to it.
  """
  def __init__(self, data: dict[str, int], fp: str=FILE_PATH):
    self.data: dict[str, int] = data
    self._fp = fp

  def select_weighted_random(self) -> str:
    """
    Pseudo-weighted random generator.

    The more often the weather is chosen before (higher int value), the less often it gets chosen.
    Returns:
      string: the weather that got chosen
    """
    if not self.data:
      raise weather_empty_error.WeatherEmptyError()
    total = sum(self.data.values())
    if total == 0:
      # empty
      return random.choice(list(self.data.keys()))
    
    weights: list[float] = []

    # Collect the information from the json, and weight each weather's probability by their counts.
    # More counts = less probability of being chosen.
    for _, count in self.data.items():
      weights.append(1/(count+1))
    return random.choices(list(self.data.keys()), weights=weights)[0]

  def statistics(self) -> WeatherStats:
    """
    Gets statistics related to the rolls.
    
    Returns:
      WeatherStats class: Format: 
      (
        Total rolls
        Percentages
        Most common weather
        Least common weather
      )
    """
    total = sum(self.data.values())
    if total == 0:
      return WeatherStats(
        total_rolls=total,
        percentages={k: 0.0 for k in self.data},
        most_common="N/A",
        least_common="N/A"
      )
    return WeatherStats(
      total_rolls=total,
      percentages={k: round(v / total * 100, 2) for k, v in self.data.items()},
      most_common=max(self.data, key=lambda k: self.data[k]),
      least_common=min(self.data, key=lambda k: self.data[k])
    )

  def increment_val(self, w: str) -> None:
    """
    Increments the int value of a weather.

    Raises:
      WeatherMissingError: weather is not found
    """
    if w not in self.data:
      raise weather_missing_error.WeatherMissingError(f"This should not have happened. A weather that doesn't exist in the dictionary was chosen.")
    self.data[w] += 1

  def add_new_weather(self, w: str) -> None:
    """
    Adds a weather to the dict.
    
    Args:
      w: the weather string to add
    Raises:
      WeatherExistsError: if weather already exists
    """
    if w in self.data:
      raise weather_exists_error.WeatherExistsError(f"Weather {w} already exists!")
    
    self.data[w] = 0

  def remove_weather(self, w: str) -> int:
    """
    Removes a specified weather.
    
    Args:
      w: the weather to remove
    Returns:
      counter: the int value related to the weather key before being removed
    Raises:
      WeatherMissingError: if weather does not exist
    """
    if w not in self.data:
      raise weather_missing_error.WeatherMissingError(f"Weather {w} cannot be removed because it does not exist. Create it first with /add_weather, you forehead.")
    
    c = self.data[w]
    del self.data[w]
    return c

  def modify_weather(self, w: str, new_c: int) -> int:
    """
    Modifies the specified weather's count.

    Args:
      w: the weather to modify
      new_c: the new count to modify the weather to. `w.count = new_c`

    Raises:
      WeatherMissingError: attempting to modify a weather that doesn't exist
      NegativeCountError: attempting to modify a weather's count to negative
    """
    if w not in self.data:
      raise weather_missing_error.WeatherMissingError(f"You cannot modify weather {w} because it does not exist. Create it first with /add_weather, you forehead.")
    if new_c < 0:
      raise negative_count_error.NegativeCountError(f"Weather {w} cannot be rolled a negative number of times, no matter how special this weather is.")
    old_c = self.data[w]
    self.data[w] = new_c
    return old_c

  def reset_data(self) -> None:
    """
    Resets the current .data to the initial data.
    
    Mostly here for debugging and testing.

    In reality, the discord api will interact directly with the file, with load/save_weather.
    """
    self.data = get_init_data().data

  def list_to_embed(self) -> de:
    """
    Turns the weather data attribute into a discord embed.

    Returns:
      Embed: 
      
      Format:
        {
          weather: count,
          ...
        }
    """
    embed = de(title="Statistics regarding weather rolls.", colour=dc.blue())
    embed = de.from_dict(self.data)

    for weather, count in self.data.items():
      embed.add_field(name=weather, value=str(count), inline=False)
    return embed

def reset_json(fp: str=FILE_PATH) -> None:
  """
  Resets weather_probabilities.json to INITDATA.
  """
  save_weather(get_init_data(), fp)

def get_weather_path() -> str:
  """
  Gets the file name and path that contains this weather.

  Should never be called except by testing. 

  The weather path is defaulted to data/weather_probabilities.json.
  """
  return FILE_PATH

def get_init_data() -> WeatherData:
  """
  Returns the initial weather data.
  """
  return WeatherData(INITDATA.copy()) # avoid mutating

def load_weather(fp: str=FILE_PATH) -> WeatherData:
  """
  Loads the weather JSON data in hash-map (dict) form, weather-number_rolled.
  If no file exists, re-creates it with initial data.
  
  Args:
    fp: optional. path to the .json file
  Returns:
    JSON object of the hash map
  """
  if not os.path.exists(fp):
    with open(fp, "w") as f:
      json.dump(INITDATA, f, indent=4)
  
  with open(fp, "r") as f:
    return WeatherData(json.load(f))

def save_weather(wd: WeatherData, fp: str=FILE_PATH):
  """
  Saves the weather data into a file, if not specified, default to data/weather_probabilities.json.
  Args:
    wd: the WeatherData object to be saved
    fp: optional. path to the .json file
  """
  with open(fp, "w") as f:
    json.dump(wd.data, f, indent=4)
