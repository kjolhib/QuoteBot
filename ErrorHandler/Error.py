import time

class Error:
  def __init__(self, error_msg, func_name):
    self.error_msg: str = error_msg
    self.func_name: str = func_name
    self.time = time.ctime(time.time())
