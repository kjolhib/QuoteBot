from exceptions.quote_bot_errors import SoftError

class InvalidFacesError(SoftError):
  """
  Exception raised when a die is created with an invalid number of faces.
  Valid numbers are either, EXACTLY 4, or any number >= 6
  """
  def __init__(self, message: str = "Invalid number of faces. Must be either 4, or any number >= 6."):
    super().__init__(message)