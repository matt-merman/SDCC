import socket
import json
import sys

from .ring import Ring, Type
from .verbose import set_logging, print_log_rx
from .bully import Bully
from .constants import BUFF_SIZE
from .helpers import create_msg, get_id


class Node:

    """
    Node class registers the current node to the network (through
    register service) and starts either ring-based or bully algorithm (defined by command line).  
    """

    def __init__(self, verbose: bool, algorithm: bool, config_path: str, delay: bool):

        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.port_register = config["register"]["port"]
        self.ip_register = config["register"]["ip"]
        self.ip = config["node"]["ip"]

        self.algorithm = algorithm   # True for bully alg.
        self.verbose = verbose
        self.logging = set_logging()
        self.delay = delay

    def start(self):

        # ephemeral socket used with register
        e_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        e_sock.bind((self.ip, 0))

        # socket used in listening phase
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, 0))
        sock.listen()
        info = sock.getsockname()
        self.port = info[1]

        if self.verbose:
            self.logging.debug("[Node]: (ip:{} port:{})\n[Triggered]\n".format(
                self.ip, self.port))

        # sends a request to join the network contacting the register node
        msg = create_msg(-1, Type['REGISTER'].value, self.port, self.ip)
        dest = (self.ip_register, self.port_register)

        e_sock.connect(dest)
        e_sock.send(msg)

        # waits to receive the complete list of network members
        data = e_sock.recv(BUFF_SIZE)
        msg = eval(data.decode('utf-8'))

        identifier = get_id(self.port, msg)

        if self.verbose:
            print_log_rx(self.logging, (self.ip, self.port),
                         dest, identifier, msg)

        # check if current node is the last one
        if (len(msg) == 1):
            e_sock.close()
            sock.close()
            print("Not enough nodes generated!")
            sys.exit(1)

        e_sock.close()

        if self.algorithm:
            Bully(self.ip, self.port, identifier,
                  msg, sock, self.verbose, self.delay, self.algorithm)
        else:
            Ring(self.ip, self.port, identifier,
                 msg, sock, self.verbose, self.delay, self.algorithm)
