import socket
import json
from . import constants as const
from . import helpers as help


class Register:

    """
    Register class provides the register service to all network members.
    Register socket is kept open for a SOCKET_TIMEOUT period.
    """

    def __init__(self, verbose: bool, config_path: str):

        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.port = config["register"]["port"]
        self.ip = config["register"]["ip"]

        self.nodes = []
        self.verbose = verbose
        self.logging = help.set_logging()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.sock.listen()
        self.connections = []

    def receive(self):

        if self.verbose:
            self.logging.debug("[Register]: (ip:{} port:{})\n[Triggered]\n".format(
                self.ip, self.port))

        list_id = []
        self.sock.settimeout(const.SOCKET_TIMEOUT)
        while True:
            try:

                conn, addr = self.sock.accept()
                data = conn.recv(const.BUFF_SIZE)
                msg = eval(data.decode('utf-8'))
                if msg["type"] != const.REGISTER:
                    continue

                # randomly generates an id for every nodes
                identifier = help.generate(list_id)

                self.connections.append(conn)
                node = dict(
                    {'ip': msg["ip"], 'port': msg["port"], 'id': identifier})
                self.nodes.append(node)

                if self.verbose:
                    help.print_log_rx(self.logging, (self.ip, self.port),
                                      addr, 0, msg)
            except socket.timeout:
                break

        self.nodes.sort(key=lambda x: x["id"])

    def send(self):

        data = str(self.nodes).encode('utf-8')
        for node in range(len(self.nodes)):

            ip = self.nodes[node]["ip"]
            port = self.nodes[node]["port"]
            identifier = self.nodes[node]["id"]
            if self.verbose:
                help.print_log_tx(self.logging, (ip, port),
                                  (self.ip, self.port), identifier, self.nodes)
            try:
                self.connections[node].send(data)
            except socket.timeout:
                print("Error: no ack from node on port {}".format(port))

        self.sock.close()

    # method used by tests class
    def get_list(self) -> list:
        return self.nodes
