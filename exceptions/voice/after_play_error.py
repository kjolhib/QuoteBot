from exceptions.quote_bot_errors import HardError

class AfterPlayError(HardError):
  """
  Exception raised when `after_play` function errored.
  """
  def __init__(self, message: str, ctx: str, ext_info: str):
    super().__init__(message, ctx, ext_info)
