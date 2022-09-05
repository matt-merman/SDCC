import time
import socket
import json
from src.algorithm import *


class Node:

    def __init__(self, id, port, type):

        self.ip_register = "192.168.1.7"
        self.port_register = 12345

        self.ip = "localhost"
        self.id = id
        self.port = port
        self.type = type

        self.algorithm = False   # True for bully alg.

    # send node's info to register node using UDP
    # and wait for complete list of participates
    def initialize(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        address = (self.ip, self.port)
        s.bind(address)

        #self.port = s.getsockname()[1]

        info = json.dumps({'ip': self.ip, 'port': self.port, 'id': self.id})
        #s.sendto(info.encode('utf-8'), (self.ip_register, self.port_register))

        # receiving
        #data, address = s.recvfrom(4096)
        #data = eval(data.decode('utf-8'))
        #print("Received: \n" + str(data))

        data = [{"ip": "localhost", "port": 54322, "id": 456},
                {"ip": "localhost", "port": 54323, "id": 789},
                {"ip": "localhost", "port": 54321, "id": 123}
                ]

        data.sort(key=lambda x: x["id"])

        Ring(self.ip, self.port, self.id, data, s)
