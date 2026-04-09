import json
import os

FILE_NAME = os.path.join(os.path.dirname(__file__), "weather_probabilities.json")
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

# Helper for DnD
def load_weather():
  """
  Loads the weather JSON data in hash-map (dict) form, weather-number_rolled.
  :return: json object of the hash map
  """
  if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w") as f:
      json.dump(INIT_DATA, f, indent=4)
  with open(FILE_NAME, "r") as f:
    return json.load(f)

def save_weather(data):
  """
  Saves the weather data after session end.
  :params data: the dictionary data to be saved
  """
  with open(FILE_NAME, "w") as f:
    json.dump(data, f, indent=4)

def get_weather_path():
  """
  Gets the file name and path
  """
  return FILE_NAME

def reset_weather_to_default():
  """
  Resets weather_probabilities.json file to INIT_DATA
  """
  try:
    save_weather(INIT_DATA)
  except Exception as e:
    print(f"reset_weather_to_default: Failed to load weather: {e}")
