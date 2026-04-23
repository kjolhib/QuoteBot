class WeatherEmptyError(Exception):
  """
  Exception raised when weather_probabilities.json is empty, and operations on key/values are called.
  """
  pass