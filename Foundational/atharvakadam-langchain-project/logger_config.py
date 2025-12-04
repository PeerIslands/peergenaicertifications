import logging
import os

def setup_logger():
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d - %(message)s"

    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT)

        # console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    return logger

logger = setup_logger()