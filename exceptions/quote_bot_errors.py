from discord import app_commands

class QuoteBotError(app_commands.AppCommandError):
  """
  Error class for handling all custom errors propagated by QuoteBot commands.

  Handled by the global on_command_error event.

  Attributes:
    `message`: the message propagated by the error. Sent as a message.
    `ctx`: the context that the error occurred. Usually the function name. Passed into report_error.
    `ext_info`: any extra info regarding the ctx and the error. Passed into report_error.
  """
  def __init__(self, message: str, ctx: str, ext_info: str):
    super().__init__(message)
    self.message: str = message
    self.ctx: str= ctx
    self.ext_info: str = ext_info

class SoftError(QuoteBotError):
  """
  A soft error propagated. Sends a specific message to the channel.

  Will not report an error to the log.
  
  Usually a well known, user-input-related error.
    For example, an edge case or requirement (e.g. `require_voice`, `require_dnd_session` decorators) not met.

  """
  def __init__(self, message: str):
    super().__init__(message, "", "") # Pass in no ctx or extra info, since it is not required and is a well known error. 

class HardError(QuoteBotError):
  """
  A hard error propagated. Sends "unknown error" to the channel.

  Will report an error. Is an error that is indicative of an actual bug in my code.
  """
  def __init__(self, message: str, ctx: str, ext_info: str):
    super().__init__(message, ctx, ext_info)
