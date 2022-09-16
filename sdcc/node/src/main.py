import socket
import json

from .ring import Ring, Type
from .verbose import set_logging, print_log_rx
from .bully import Bully
from .constants import BUFF_SIZE
from .helpers import create_msg, get_id


class Node:

    def __init__(self, verbose, algorithm, config_path):

        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.port_register = config["register"]["port"]
        self.ip_register = config["register"]["ip"]

        self.ip = "localhost"
        self.port = None
        self.algorithm = algorithm   # True for bully alg.
        self.verbose = verbose
        self.logging = set_logging()

    # send node's info to register node using UDP
    # and wait for complete list of participates

    def start(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address = (self.ip, 0)
        s.bind(address)

        info = s.getsockname()
        self.port = info[1]

        if self.verbose:
            self.logging.debug("[Node]: (ip:{} port:{})\n[Triggered]\n".format(
                self.ip, self.port))

        msg = create_msg(-1, Type['REGISTER'].value, self.port, self.ip)
        dest = (self.ip_register, self.port_register)
        s.sendto(msg, dest)

        msg, addr = s.recvfrom(BUFF_SIZE)
        msg = eval(msg.decode('utf-8'))
        identifier = get_id(self.port, msg)

        if self.verbose:
            print_log_rx(self.logging, (self.ip, self.port),
                         addr, identifier, msg)

        if self.algorithm:
            Bully(self.ip, self.port, identifier, msg, s, self.verbose)
        else:
            Ring(self.ip, self.port, identifier, msg, s, self.verbose)
