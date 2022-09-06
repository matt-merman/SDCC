import socket
import json
from .ring import *


class Node:

    def __init__(self):

        with open("../config.json", "r") as config_file:
            config = json.load(config_file)

        self.port_register = config["register"]["port"]
        self.ip_register = config["register"]["ip"]

        self.ip = "localhost"
        self.port = None
        self.algorithm = False   # True for bully alg.

    # send node's info to register node using UDP
    # and wait for complete list of participates
    def initialize(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        address = (self.ip, 0)
        s.bind(address)

        info = s.getsockname()
        self.port = info[1]

        s.sendto("".encode('utf-8'), (self.ip_register, self.port_register))

        data, address = s.recvfrom(4096)
        data = eval(data.decode('utf-8'))
        print("Received: \n" + str(data))

        id = get_id(self.port, data)
        Ring(self.ip, self.port, id, data, s)
