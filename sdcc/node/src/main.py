import time
import socket
import json
from ping3 import ping, verbose_ping
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

        data = ['{"ip": "localhost", "port": 54321, "id": 1}', 
                '{"ip": "localhost", "port": 54322, "id": 2}',
                '{"ip": "localhost", "port": 54323, "id": 3}'
                ]

        ring = Ring(self.ip, self.port, self.id, data, s)
        if self.type: ring.starting()
        else: ring.listening()

    def heartbeat(self, nodes_list):

        # try to ping all nodes in the network
        for node in range(len(nodes_list)):

            info = json.loads(nodes_list[node])
            ip = info["ip"]
            id = info["id"]
            if ping(ip) == None:
                print("No reply!")
            else:
                print("Reply!")
