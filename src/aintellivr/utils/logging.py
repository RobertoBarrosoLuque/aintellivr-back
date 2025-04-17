import logging
from functools import wraps

_PROJECT_LOGGER_NAME = "aintellivr"


def get_logger():
    """
    Helper function to set up logger for print-only logging.
    :return:
    """
    _logger = logging.getLogger(_PROJECT_LOGGER_NAME)
    _logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(filename)s: %(funcName)s %(lineno)d: %(message)s",
        datefmt="%Y/%m/%d-%I:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    _logger.addHandler(stream_handler)

    _logger.propagate = False

    return _logger


logger = get_logger()


def print(message: str, level: str = "info"):
    getattr(logger, level)(message)


def basic_logging(function):
    """
    Decorator for basic logging of function. Logs start of function execution and end of function execution
    :param function:
    :return:
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            logger.info(f"Starting execution of function {function.__name__}")
            obj = function(*args, **kwargs)
        except Exception as e:
            logger.info(f"{function.__name__} failed with exception {e}")
            raise e
        logger.info(f"Successfully finished execution of function {function.__name__}")
        return obj

    return wrapper
