from exceptions.quote_bot_errors import HardError

class NoVoiceClientError(HardError):
  """
  Exception raised when a voice client was not found.
  """
  def __init__(self, message: str, ctx: str, ext_info: str):
    super().__init__(message, ctx, ext_info)
