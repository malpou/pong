import logging


def setup_logger():
    log = logging.getLogger("pong")

    if not log.handlers:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.asgi").setLevel(logging.WARNING)

        log.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)

        log.addHandler(console_handler)
        log.propagate = False

    return log

logger = setup_logger()