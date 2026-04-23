class WeatherMissingError(Exception):
  """
  Exception raised when a weather is missing in the weather_probabilities.json file, and operations relating to removing/operating on this scenario is called.
  """
  pass