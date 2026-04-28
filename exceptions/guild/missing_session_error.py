from exceptions.quote_bot_errors import HardError

class MissingSessionError(HardError):
  """
  Exception raised when a session was expected, but found null or None.
  """
  def __init__(self, message: str, ctx: str, ext_info: str):
    super().__init__(message, ctx, ext_info)