from exceptions.quote_bot_errors import SoftError

class DieAlrExistsError(SoftError):
  """
  Exception raised when a die with the same scenario already exists.
  """
  def __init__(self, message: str = "Die with the same scenario already exists."):
    super().__init__(message)
