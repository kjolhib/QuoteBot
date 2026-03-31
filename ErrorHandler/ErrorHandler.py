import time
import logging
from .Error import Error
from logging.handlers import RotatingFileHandler

LOG_PATH = "QuoteBot_errors.log"

# Keep last 5 logs, max 1mb size
handler = RotatingFileHandler (
  LOG_PATH,
  maxBytes=1_000_000,
  backupCount=5
)

logging.basicConfig(
  level=logging.ERROR,
  format="%(asctime)s [%(name)s %(filename)s:%(lineno)d] %(levelname)s: %(message)s",
  handlers=[handler]
)

def log_error(error: Error):
  print(error)
  logging.error("[%s] %s", error.func_name.upper(), error.error_msg, stacklevel=3)

def report_exception(f_name: str):
  try:
    logging.exception(f"[ERROR]: traceback: [{f_name.upper()}] crashed")
  except Exception as e:
    print(f"FATAL ERROR: report_exception failed: {e}")

def report_error(error: Error):
  try:
    print(f"[ERROR: {error.time}]: [{(error.func_name).upper()}]: {error.error_msg}")
    log_error(error)
  except Exception as e:
    return print(f"[FATAL ERROR: {time.time()}]: report_error: {e}")
