import logging


LOGGER = logging.getLogger(__name__)


def create_root_logger():
    """Create root logger.
    Import something from 'utilia' to trigger 'create_root_logger' execution.
    Or:
        from utilia import create_root_logger
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    log_formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(funcName)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # remove existing loggers as function called multiple times
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)

    root_logger.addHandler(console_handler)

    # disable "py4j.java_gateway:Received command c on object id p0"
    logging.getLogger("py4j").setLevel(logging.ERROR)

    LOGGER.info("Root logger created")


create_root_logger()
