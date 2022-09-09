from enum import Enum
import socket
import time
from .verbose import *
from .helpers import *
from .constants import *


class Type(Enum):
    ELECTION = 0
    COORDINATOR = 2
    ACK = 3
    STOP = 4
    HEARTBEAT = 5


class Algorithm():

    def __init__(self, ip, port, id, nodes, socket, verbose):

        self.verbose = verbose
        self.ip = ip
        self.port = port
        self.id = id
        self.nodes = nodes
        self.socket = socket
        self.coordinator = None

        self.logging = set_logging()
        self.participant = False

    def heartbeat(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        address = (self.ip, 0)
        s.bind(address)
        address = self.socket.getsockname()

        while True:

            time.sleep(HEARTBEAT_TIME)
            if self.coordinator == self.id:
                continue

            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nStarts Heartbeat\n".format(
                    self.ip, self.port, self.id))

            index = get_index(self.coordinator, self.nodes)
            info = self.nodes[index]
            dest = (info["ip"], info["port"])
            self.forwarding(
                s, self.id, Type['HEARTBEAT'].value, dest, (address[0], address[1]))
            s.settimeout(TOTAL_DELAY)

            try:
                data, _ = s.recvfrom(BUFF_SIZE)
                data = eval(data.decode('utf-8'))
                if data["type"] == Type["ACK"].value:
                    if self.verbose:
                        self.logging.debug("Node: (ip:{} port:{} id:{})\nEnds Heartbeat\n".format(
                            self.ip, self.port, self.id))
                    continue
                else:
                    print("Wrong packet received\n")
                    s.settimeout(None)
                    self.start_election()

            except socket.timeout:
                print("timeout for ACK\n")
                s.settimeout(None)
                self.start_election()

    def forwarding(self, socket, id, type, dest, sender):
        msg = create_msg(id, type, sender[1], sender[0])
        socket.sendto(msg, dest)
