from exceptions.quote_bot_errors import SoftError

class UserInStageVcError(SoftError):
  """
  Exception raised when the user is in a stage VC and join is called
  """
  def __init__(self, message: str = "User in stage VC. I cannot join stage vc's. If you REALLY want me tho... choose a different place to hang!"):
    super().__init__(message)
