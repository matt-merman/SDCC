import json
import sys

from .ring import Ring, Type
from .verbose import set_logging, print_log_rx
from .bully import Bully
from .constants import BUFF_SIZE
from .helpers import create_msg, get_id, create_socket


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
        self.delay = delay

    def start(self):

        # ephemeral socket used with register
        ephemeral_sock = create_socket(self.ip)

        # socket used in listening phase
        sock = create_socket(self.ip)
        sock.listen()

        logging = set_logging()

        if self.verbose:
            logging.debug("[Node]: (ip:{} port:{})\n[Triggered]\n".format(
                sock.getsockname()[0], sock.getsockname()[1]))

        # sends a request to join the network contacting the register node
        msg = create_msg(-1, Type['REGISTER'].value,
                         sock.getsockname()[1], sock.getsockname()[0])
        dest = (self.ip_register, self.port_register)

        ephemeral_sock.connect(dest)
        ephemeral_sock.send(msg)

        # waits to receive the complete list of network members
        data = ephemeral_sock.recv(BUFF_SIZE)
        msg = eval(data.decode('utf-8'))
        identifier = get_id(sock.getsockname()[1], msg)

        print_log_rx(self.verbose, logging, (self.ip, sock.getsockname()[1]),
                     dest, identifier, msg)

        ephemeral_sock.close()

        # check if current node is the last one
        if (len(msg) == 1):
            sock.close()
            print("Not enough nodes generated!")
            sys.exit(1)

        if self.algorithm:
            Bully(self.ip, sock.getsockname()[1], identifier,
                  msg, sock, self.verbose, self.delay, self.algorithm)
        else:
            Ring(self.ip, sock.getsockname()[1], identifier,
                 msg, sock, self.verbose, self.delay, self.algorithm)
