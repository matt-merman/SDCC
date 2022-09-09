from enum import Enum
import time
import threading as thr

from .verbose import *
from .helpers import *

# type: 0 - starting election, 1 - ending election, 2 - heartbeat, 3 - ACK

HEARTBEAT_TIME = 5


class Type(Enum):
    STARTING = 0
    ENDING = 1
    HEARTBEAT = 2
    ACK = 3


class Ring():

    def __init__(self, ip, port, id, nodes, socket, verbose):

        self.verbose = verbose
        self.ip = ip
        self.port = port
        self.id = id
        self.nodes = nodes
        self.socket = socket
        self.coordinator = False

        # initially, every process is marked as a non-participant in an election
        self.participant = True
        self.ack = False
        self.logging = set_logging()
        # thread is listening for msg
        # time.sleep(10)
        thread = thr.Thread(target=self.listening)
        thread.start()

        self.heartbeat()

    def end(self, data):
        if self.coordinator != self.id:
            self.participant = False
            self.coordinator = data["id"]
            dest = get_dest(self.id, self.nodes)
            self.forwarding(data, Type['ENDING'].value, dest)

    def ack(self, data):
        ip_dest = data["ip"]
        port_dest = data["port"]
        dest = (ip_dest, port_dest)
        self.forwarding(self.id, Type['ACK'].value, dest)
        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{})\nReceived Ack\n".format(
                self.ip, self.port, self.id))

    def receiving(self, data):

        id = data["id"]
        self.participant = True
        dest = get_dest(self.id, self.nodes)

        if id < self.id:

            if self.participant == False:
                data["id"] = self.id
            else:
                self.participant = False
                return

        elif id == self.id:
            self.participant = False
            self.coordinator = self.id
            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nElected as Coordinator\n".format(
                    self.ip, self.port, self.id))

            self.forwarding(data["id"], Type['ENDING'].value, dest)
            return

        self.forwarding(data["id"], Type['STARTING'].value, dest)

    def listening(self):

        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{})\nStarts election\n".format(
                self.ip, self.port, self.id))

        dest = get_dest(self.id, self.nodes)
        self.forwarding(self.id, Type['STARTING'].value, dest)

        while True:

            data, address = self.socket.recvfrom(4096)
            data = eval(data.decode('utf-8'))

            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nSender: (ip:{} port:{})\nMessage: {}\n".format(
                    self.ip, self.port, self.id, address[0], address[1], data))

            type_one = Type['STARTING'].value
            type_two = Type['ENDING'].value
            type_three = Type['ACK'].value

            if data["type"] == Type['HEARTBEAT'].value:
                self.ack = True
                continue

            type = {type_one: self.receiving,
                    type_two: self.end,
                    type_three: self.ack,
                    }

            type[data["type"]](data)

    def heartbeat(self):

        while True:

            time.sleep(HEARTBEAT_TIME)

            if self.participant or (self.coordinator == self.id):
                continue

            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nStarts Election\n".format(
                    self.ip, self.port, self.id))

            index = get_index(self.coordinator, self.nodes)
            info = self.nodes[index]
            dest = (info["ip"], info["port"])
            self.forwarding(self.id, Type['HEARTBEAT'].value, dest)

            # waiting util it receives the ack
            while not self.ack:
                None

            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nEnds Election\n".format(
                    self.ip, self.port, self.id))

    def forwarding(self, id, type, dest):
        msg = create_msg(id, type, 0, self.ip)
        self.socket.sendto(msg, dest)
