from exceptions.quote_bot_errors import SoftError

class UserNotInVcError(SoftError):
  """
  Exception raised when the user isn't in VC and join is called
  """
  def __init__(self, message: str = "You must be in a VC to invite me one! Don't send an invitation to a party you aren't even invited to :("):
    super().__init__(message)
