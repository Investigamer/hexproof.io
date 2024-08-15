# Standard Library Imports
import logging

# Third Party Imports
from omnitils.logs import logger


class LoguruHandler(logging.Handler):
    """Acts as a compatibility layer intercepting logging messages and passing them appropriately
        to our loguru logger object."""

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the log message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# Add the handler to the root logger
logging.basicConfig(handlers=[LoguruHandler()], level=logging.INFO)
