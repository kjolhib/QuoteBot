from exceptions.quote_bot_errors import SoftError

class TimeFormatError(SoftError):
  """
  Exception raised when the time format is incorrect.
  Should be HH:MM
  """
  def __init__(self, message: str = "Time is not in the format HH:MM."):
    super().__init__(message)
