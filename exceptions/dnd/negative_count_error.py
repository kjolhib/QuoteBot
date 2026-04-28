from exceptions.quote_bot_errors import SoftError

class NegativeCountError(SoftError):
  """
  Exception raised when a weather is attempting to be modified to a negative count.
  """
  def __init__(self, message: str = "You cannot change the weather count to a negative number."):
    super().__init__(message)