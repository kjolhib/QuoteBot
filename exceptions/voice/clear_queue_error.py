from exceptions.quote_bot_errors import HardError

class ClearQueueError(HardError):
  """
  Exception raised when clearing the queue fails.
  """
  def __init__(self, message: str, ctx: str, ext_info: str):
    super().__init__(message, ctx, ext_info)
