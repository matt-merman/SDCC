import logging


def set_logging() -> logging:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(asctime)s\n%(message)s",
        datefmt='%b-%d-%y %I:%M:%S'
    )

    return logging


def print_log_rx(flag: bool, logging: logging, receiver: tuple, sender: tuple, id: int, data: list):

    if flag:
        logging.debug("[Node]: (ip:{} port:{} id:{})\n[Sender]: (ip:{} port:{})\n[Message]: {}\n".format(
            receiver[0], receiver[1], id, sender[0], sender[1], data))


def print_log_tx(flag: bool, logging: logging, receiver: tuple, sender: tuple, id: int, data: list):

    if flag:
        logging.debug("[Node]: (ip:{} port:{} id:{})\n[Receiver]: (ip:{} port:{})\n[Message]: {}\n".format(
            sender[0], sender[1], id, receiver[0], receiver[1], data))
