import logging
from config import LOG_LEVEL

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)-8s] %(module)8s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)
    return logger
