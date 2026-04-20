class DateFormatError(Exception):
  """
  Exception raised when the date format is wrong.
  Should be DD/MM/YYYY
  """
  def __init__(self, msg: str):
    super().__init__(msg)

# try:
#   raise DateFormatError("Failed to clear the queue due to an unexpected error.")
# except DateFormatError as itfe:
#   print(f"Error: {itfe}")