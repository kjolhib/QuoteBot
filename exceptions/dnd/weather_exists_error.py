class WeatherExistsError(Exception):
  """
  Exception raised when a weather already exists in the weather_probabilities.json file, and operations relating to adding this scenario is called.
  """
  pass