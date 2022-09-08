import socket
import time
from threading import Thread
from random import randint
import json

from .constants import *
from .verbose import *


class Register:

    def __init__(self, verbose):

        self.address_nodes = []
        self.log = []
        self.socket = None
        self.verbose = verbose
        self.logging = set_logging()
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

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('localhost', 0)
        self.socket.bind(server_address)
        info = self.socket.getsockname()
        self.update_conf(info[1])

        if self.verbose:
            self.logging.debug("Register: (ip:{} port:{})\n".format(
                info[0], info[1]))

        thread = Thread(target=self.receive)
        thread.start()

        # in listening for a while
        timeout = time.time() + RECEPTION_WINDOW
        while time.time() < timeout:
            continue

        self.send()

    def send(self):

        self.log.sort(key=lambda x: x["id"])

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('localhost', 0)
        s.bind(server_address)

        info = s.getsockname()

        for node in range(len(self.address_nodes)):

            addr = self.address_nodes[node][0]
            port = self.address_nodes[node][1]
            data = str(self.log).encode('utf-8')
            s.sendto(data, (addr, port))

        if self.verbose:
            self.logging.debug("Register: (ip:{} port:{}))\nmessage: {}\n".format(
                info[0], info[1], data))

        s.close()

    def update_conf(self, port):
        with open("../config.json", "r+") as jsonFile:
            data = json.load(jsonFile)
            data["register"]["port"] = port
            jsonFile.seek(0)  # rewind
            json.dump(data, jsonFile)
            jsonFile.truncate()
