from enum import Enum
import socket
import time
from .verbose import *
from .helpers import *
from .constants import *
from abc import ABC, abstractmethod
from threading import *


class Type(Enum):
    ELECTION = 0
    END_ELECT = 1
    ACK = 2
    HEARTBEAT = 3


class Algorithm(ABC):

    def __init__(self, ip, port, id, nodes, socket, verbose):

        self.verbose = verbose
        self.ip = ip
        self.port = port
        self.id = id
        self.nodes = nodes
        self.socket = socket
        self.coordinator = -1

        self.logging = set_logging()
        self.participant = False

        self.number_crashes = 1

        thread = Thread(target=self.listening)
        thread.start()
        self.start_election()
        Algorithm.heartbeat(self)

    @abstractmethod
    def start_election(self):
        pass

    @abstractmethod
    def end_election(self):
        pass

    @abstractmethod
    def election_msg(self):
        pass

    def listening(self):

        while True:

            data, address = self.socket.recvfrom(BUFF_SIZE)
            data = eval(data.decode('utf-8'))

            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nSender: (ip:{} port:{})\nMessage: {}\n".format(
                    self.ip, self.port, self.id, address[0], address[1], data))

            if data["type"] == Type['HEARTBEAT'].value:
                Algorithm.forwarding(
                    self, self.id, Type['ACK'].value, address)
                continue

            type = {Type['ELECTION'].value: self.election_msg,
                    Type['END_ELECT'].value: self.end_election
                    }

            type[data["type"]](data)

    def crash(self, socket):
        socket.settimeout(None)
        self.number_crashes += 1
        # remove the last node (a.k.a coordinator)
        self.nodes.pop()
        self.start_election()

    def heartbeat(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        address = (self.ip, 0)
        s.bind(address)
        address = s.getsockname()

        while True:

            time.sleep(HEARTBEAT_TIME)

            if self.participant or (self.coordinator == self.id):
                continue

            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nStarts Heartbeat\n".format(
                    address[0], address[1], self.id))

            index = get_index(self.coordinator, self.nodes)
            info = self.nodes[index]
            dest = (info["ip"], info["port"])

            msg = create_msg(
                self.id, Type['HEARTBEAT'].value, address[1], address[0])
            s.sendto(msg, dest)

            s.settimeout(TOTAL_DELAY)

            try:
                data, _ = s.recvfrom(BUFF_SIZE)
                data = eval(data.decode('utf-8'))
                if data["type"] == Type["ACK"].value:
                    if self.verbose:
                        self.logging.debug("Node: (ip:{} port:{} id:{})\nEnds Heartbeat\n".format(
                            address[0], address[1], self.id))
                    continue
                else:
                    self.crash(s)

            except socket.timeout:
                self.crash(s)

    def forwarding(self, id, type, dest):
        msg = create_msg(id, type, self.port, self.ip)
        self.socket.sendto(msg, dest)
