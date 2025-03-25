import logging
import sys


def setup_logging():
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler]
    )

    loggers_to_quiet = [
        'sqlalchemy.engine',
        'sqlalchemy.orm',
        'uvicorn',
        'uvicorn.access',
        'uvicorn.error',
        'fastapi'
    ]

    for logger_name in loggers_to_quiet:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str):
    logger = logging.getLogger(name)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

    return logger
