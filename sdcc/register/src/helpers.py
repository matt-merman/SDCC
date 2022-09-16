import logging
from random import randint
from . import constants as const


def generate(list):
    identifier = randint(const.MIN, const.MAX)
    if identifier not in list:
        return identifier
    else:
        generate(list)


def set_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(asctime)s\n%(message)s",
        datefmt='%b-%d-%y %I:%M:%S'
    )
    return logging


def print_log_rx(logging, receiver, sender, id, data):
    logging.debug("[Node]: (ip:{} port:{} id:{})\n[Sender]: (ip:{} port:{})\n[Message]: {}\n".format(
        receiver[0], receiver[1], id, sender[0], sender[1], data))


def print_log_tx(logging, receiver, sender, id, data):
    logging.debug("[Node]: (ip:{} port:{} id:{})\n[Receiver]: (ip:{} port:{})\n[Message]: {}\n".format(
        sender[0], sender[1], id, receiver[0], receiver[1], data))
