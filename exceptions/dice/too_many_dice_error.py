from exceptions.quote_bot_errors import SoftError

class TooManyDiceError(SoftError):
  """
  Exception raised when there are too many dice in the session.
  """
  def __init__(self, message: str = "You cannot create more than 100 dice per session. Contact @chewswisely with a very good reason if you believe you somehow need more."):
    super().__init__(message)

