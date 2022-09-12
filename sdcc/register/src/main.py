import socket
import time
from threading import Thread
from random import randint
import json

from .constants import *
from .helpers import *


class Register:

    def __init__(self, verbose):

        self.address_nodes = []
        self.log = []
        self.socket = None
        self.verbose = verbose
        self.logging = set_logging()
        self.ip = None
        self.start()

    def receive(self):

        self.socket.settimeout(SOCKET_TIMEOUT)
        while True:
            try:
                _, addr = self.socket.recvfrom(4096)
                id = randint(MIN, MAX)
                node = dict({'ip': addr[0], 'port': addr[1], 'id': id})
                self.log.append(node)
                self.address_nodes.append(addr)

            except socket.timeout:
                break

        self.socket.close()

    def start(self):

        with open("./config.json", "r") as config_file:
            config = json.load(config_file)

        port = config["register"]["port"]
        self.ip = config["register"]["ip"]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.ip, port)
        self.socket.bind(server_address)
        info = self.socket.getsockname()

        if self.verbose:
            self.logging.debug("Register: (ip:{} port:{})\n".format(
                info[0], info[1]))

        self.receive()
        self.send()

    def send(self):

        self.log.sort(key=lambda x: x["id"])

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.ip, 0)
        s.bind(server_address)

        info = s.getsockname()

        for node in range(len(self.address_nodes)):

            addr = self.address_nodes[node][0]
            port = self.address_nodes[node][1]
            data = str(self.log).encode('utf-8')
            s.sendto(data, (addr, port))

        if self.verbose:
            self.logging.debug("Register: (ip:{} port:{}))\nmessage: {}\n".format(
                info[0], info[1], str(self.log).encode('utf-8')))

        s.close()
