import socket
import json
from random import randint
from . import constants as const
from . import helpers as help


class Register:

    def __init__(self, verbose, config_path):

        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.port = config["register"]["port"]
        self.ip = config["register"]["ip"]

        self.nodes = []
        self.socket = None
        self.verbose = verbose
        self.logging = help.set_logging()

    def receive(self):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.ip, self.port)
        self.socket.bind(server_address)

        if self.verbose:
            self.logging.debug("[Register]: (ip:{} port:{})\n[Triggered]\n".format(
                self.ip, self.port))

        self.socket.settimeout(const.SOCKET_TIMEOUT)
        while True:
            try:
                msg, addr = self.socket.recvfrom(const.BUFF_SIZE)
                id = randint(const.MIN, const.MAX)
                node = dict({'ip': addr[0], 'port': addr[1], 'id': id})
                self.nodes.append(node)
                msg = eval(msg.decode('utf-8'))

                if self.verbose:
                    help.print_log_rx(self.logging, (self.ip, self.port),
                                      addr, -1, msg)

            except socket.timeout:
                break

        self.nodes.sort(key=lambda x: x["id"])

    def send(self):

        data = str(self.nodes).encode('utf-8')
        for node in range(len(self.nodes)):

            ip = self.nodes[node]["ip"]
            port = self.nodes[node]["port"]
            id = self.nodes[node]["id"]
            if self.verbose:
                help.print_log_tx(self.logging, (ip, port),
                                  (self.ip, self.port), id, self.nodes)
            self.socket.sendto(data, (ip, port))

        self.socket.close()

    def get_list(self):
        return self.nodes
