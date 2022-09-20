import socket
import json
from . import constants as const
from . import helpers as help


class Register:

    def __init__(self, verbose: bool, config_path: str):

        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.port = config["register"]["port"]
        self.ip = config["register"]["ip"]

        self.nodes = []
        self.verbose = verbose
        self.logging = help.set_logging()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.ip, self.port)
        self.socket.bind(server_address)

    def receive(self):

        if self.verbose:
            self.logging.debug("[Register]: (ip:{} port:{})\n[Triggered]\n".format(
                self.ip, self.port))

        list_id = []
        self.socket.settimeout(const.SOCKET_TIMEOUT)
        while True:
            try:
                msg, addr = self.socket.recvfrom(const.BUFF_SIZE)
                identifier = help.generate(list_id)
                node = dict({'ip': addr[0], 'port': addr[1], 'id': identifier})
                self.nodes.append(node)
                msg = eval(msg.decode('utf-8'))

                if msg["type"] != const.REGISTER:
                    continue

                if self.verbose:
                    help.print_log_rx(self.logging, (self.ip, self.port),
                                      addr, 0, msg)

            except socket.timeout:
                break

        self.nodes.sort(key=lambda x: x["id"])

    def send(self):

        msg = str(self.nodes).encode('utf-8')
        for node in range(len(self.nodes)):

            ip = self.nodes[node]["ip"]
            port = self.nodes[node]["port"]
            identifier = self.nodes[node]["id"]
            if self.verbose:
                help.print_log_tx(self.logging, (ip, port),
                                  (self.ip, self.port), identifier, self.nodes)
            self.socket.sendto(msg, (ip, port))

        self.socket.close()

    def get_list(self) -> list:
        return self.nodes
