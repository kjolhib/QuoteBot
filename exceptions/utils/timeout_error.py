from exceptions.quote_bot_errors import HardError

class TimeoutError(HardError):
  """
  Exception raised when a command times out.
  """
  def __init__(self, message: str, ctx: str, ext_info: str):
    super().__init__(message, ctx, ext_info)