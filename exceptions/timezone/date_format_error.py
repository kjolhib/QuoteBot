from exceptions.quote_bot_errors import SoftError

class DateFormatError(SoftError):
  """
  Exception raised when the date format is wrong.
  Should be DD/MM/YYYY
  """
  def __init__(self, message: str = "Date is not in the format DD/MM/YYYY."):
    super().__init__(message)