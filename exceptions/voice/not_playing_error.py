from exceptions.quote_bot_errors import SoftError

class NotPlayingError(SoftError):
  """
  Exception raised when bot should be playing a song but is not.
  """
  def __init__(self, message: str):
    super().__init__(message)
