class InvalidFacesError(Exception):
  """
  Exception raised when a die is created with an invalid number of faces.
  Valid numbers are either, EXACTLY 4, or any number >= 6
  """
  pass