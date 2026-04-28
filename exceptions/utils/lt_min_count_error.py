from exceptions.quote_bot_errors import SoftError

class LTMinCountError(SoftError):
  """
  Exception raised when /random_message finds that a user has sent less messages than min_count
  """
  def __init__(self, message: str = "Unfortunate, that user has sent too few messages recently!"):
    super().__init__(message)