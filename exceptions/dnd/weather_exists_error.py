from exceptions.quote_bot_errors import SoftError

class WeatherExistsError(SoftError):
  """
  Exception raised when a weather already exists in the weather_probabilities.json file, and operations relating to adding this scenario is called.
  """
  def __init__(self, message: str = "You cannot add a weather that already exists."):
    super().__init__(message)