import socket
import json

from .ring import Ring, Type
from .helpers import set_logging
from .bully import Bully
from .constants import BUFF_SIZE
from .helpers import create_msg, get_id,  print_log_rx


class Node:

    def __init__(self, verbose, algorithm):

        with open("./config.json", "r") as config_file:
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

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        address = (self.ip, 0)
        s.bind(address)

        info = s.getsockname()
        self.port = info[1]

        if self.verbose:
            self.logging.debug("[Node]: (ip:{} port:{})\n[Triggered]\n".format(
                self.ip, self.port))

        msg = create_msg(0, Type['REGISTER'].value, self.port, self.ip)
        dest = (self.ip_register, self.port_register)
        s.sendto(msg, dest)

        data, addr = s.recvfrom(BUFF_SIZE)
        data = eval(data.decode('utf-8'))
        id = get_id(self.port, data)

        if self.verbose:
            print_log_rx(self.logging, (self.ip, self.port),
                         addr, id, data)

        if self.algorithm:
            Bully(self.ip, self.port, id, data, s, self.verbose)
        else:
            Ring(self.ip, self.port, id, data, s, self.verbose)
