from exceptions.quote_bot_errors import SoftError

class NullSessionError(SoftError):
  """
  Exception raised when an operation, such as /end, attempted to fetch DnDSession data when it was null.
  """
  def __init__(self, message: str = "DnDSession was fund to be null."):
    super().__init__(message)