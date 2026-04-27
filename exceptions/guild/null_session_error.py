class NullSessionError(Exception):
  """
  Exception raised when an operation, such as /end, attempted to fetch DnDSession data when it was null.
  """
  pass