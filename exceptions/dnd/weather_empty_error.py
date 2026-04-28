from exceptions.quote_bot_errors import SoftError

class WeatherEmptyError(SoftError):
  """
  Exception raised when weather_probabilities.json is empty, and operations on key/values are called.
  """
  def __init__(self, message: str = "There are no weathers here! Create some with /add_weather, or reset with /reset_weather"):
    super().__init__(message)