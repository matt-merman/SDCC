import logging


def set_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(asctime)s\n%(message)s",
        datefmt='%b-%d-%y %I:%M:%S'
    )
    return logging
