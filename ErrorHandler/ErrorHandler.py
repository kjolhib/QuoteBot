# ErrorHandler.py
import logging
from logging.handlers import RotatingFileHandler

LOG_PATH = "QuoteBot_errors.log"
_logger = logging.getLogger("QuoteBot")

def configure_logging():
    """Call once at bot startup."""
    handler = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=5)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(name)s %(filename)s:%(lineno)d] %(levelname)s: %(message)s"
    ))
    _logger.setLevel(logging.ERROR)
    _logger.addHandler(handler)

def report_error(context: str, exc: Exception | None = None, extra_info: str | None = None):
    """
    Log an error with optional exception info.
    
    context: human-readable label, e.g. the function/command name
    exc:     the caught exception, if any (enables traceback logging)
    """
    msg = f"[{context.upper()}]" + (f": {extra_info}" if extra_info else ": No extra info available.")
    _logger.error(msg, exc_info=exc)
    print(f"[ERROR]: {context}, {extra_info}: {exc if exc else 'An unknown error occurred.'}")