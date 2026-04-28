from exceptions.quote_bot_errors import SoftError

class WeatherMissingError(SoftError):
  """
  Exception raised when a weather is missing in the weather_probabilities.json file, and operations relating to removing/operating on this scenario is called.
  """
  def __init__(self, message: str = "Weather does not exist, you cannot operate on this weather."):
    super().__init__(message)