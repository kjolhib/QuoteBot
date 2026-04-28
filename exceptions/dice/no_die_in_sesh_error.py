from exceptions.quote_bot_errors import SoftError

class NoDieInSeshError(SoftError):
  """
  Exception raised when there are no dice in the session.
  """
  def __init__(self, message: str = "No dice exists in current session. Create some with /new_dice!"):
    super().__init__(message)
