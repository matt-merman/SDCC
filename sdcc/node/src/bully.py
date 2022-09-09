from enum import Enum
import time
import threading as thr
import socket

from .verbose import *
from .helpers import *

HEARTBEAT_TIME = 5

MAX_TRANSMISSION_DELAY = 5
MAX_PROCESSING_DELAY = 1
TOTAL_DELAY = (2 * MAX_TRANSMISSION_DELAY) + MAX_PROCESSING_DELAY
BUFF_SIZE = 4096


class Type(Enum):
    ELECTION = 0
    ANSWER = 1
    COORDINATOR = 2
    ACK = 3
    STOP = 4
    HEARTBEAT = 5


class Bully():

    def __init__(self, ip, port, id, nodes, socket, verbose):

        self.verbose = verbose
        self.ip = ip
        self.port = port
        self.id = id
        self.nodes = nodes
        self.socket = socket
        self.coordinator = False

        self.logging = set_logging()
        self.participant = False

        self.ack_nodes = []
        self.number_initial_nodes = 0

        info = self.nodes[len(self.nodes) - 1]
        if info["id"] == self.id:
            self.coordinator = self.id
            self.announce_coord()
        else:
            self.end()

        # thread is listening for msg
        thread = thr.Thread(target=self.starting)
        thread.start()

        self.heartbeat()

    # sends a coordinator message to all
    # processes with lower identifiers

    def announce_coord(self):

        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{}))\nSend Election messages\n".format(
                self.ip, self.id, self.id))

        for node in range(len(self.nodes) - 1):
            dest = (self.nodes[node]["ip"], self.nodes[node]["port"])
            self.forwarding(self.id, Type['COORDINATOR'].value, dest)

    def end(self):

        self.socket.settimeout(TOTAL_DELAY)
        while True:
            try:
                data, addr = self.socket.recvfrom(BUFF_SIZE)
                data = eval(data.decode('utf-8'))
                if data["type"] == Type['COORDINATOR'].value:
                    self.coordinator = data["id"]

                if self.verbose:
                    self.logging.debug("Node: (ip:{} port:{} id:{})\nSender: (ip:{} port:{})\nMessage: {}\n".format(
                        self.ip, self.port, self.id, addr[0], addr[1], data))

                self.socket.settimeout(None)
                break
            except socket.timeout:
                self.socket.settimeout(None)
                self.start_election()

    def start_election(self):
        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{}))\nStart Election\n".format(
                self.ip, self.port, self.id))

        self.participant = True
        index = get_index(self.id, self.nodes)
        index += 1

        self.number_initial_nodes = len(self.nodes) - index

        for node in range(index, len(self.nodes)):
            dest = (self.nodes[node]["ip"], self.nodes[node]["port"])
            self.ack_nodes.append(self.nodes[node]["id"])
            self.forwarding(self.id, Type['ELECTION'].value, dest)

        # in listening for a while
        timeout = time.time() + TOTAL_DELAY
        while time.time() < timeout:
            continue

        # if node do not received ack, will be the coordinator
        if self.number_initial_nodes == len(self.ack_nodes):
            self.announce_coord()
            self.coordinator = self.id
            print("End election (new coord: {})\n".format(self.coordinator))

    def ack(self, data):
        ip_dest = data["ip"]
        port_dest = data["port"]
        dest = (ip_dest, port_dest)
        self.forwarding(self.id, Type['ACK'].value, dest)
        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{})\nReceived Ack\n".format(
                self.ip, self.port, self.id))

    def starting(self):

        while True:

            data, address = self.socket.recvfrom(BUFF_SIZE)
            data = eval(data.decode('utf-8'))

            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nSender: (ip:{} port:{})\nMessage: {}\n".format(
                    self.ip, self.port, self.id, address[0], address[1], data))

            if data["type"] == Type['ELECTION'].value:
                id = get_id(address[1], self.nodes)
                if id < self.id:
                    self.forwarding(self.id, Type['STOP'].value, address)
                    if self.participant == False:
                        self.participant = True
                        self.start_election()

            if data["type"] == Type['STOP'].value:
                self.ack_nodes = []
                self.participant = False
                self.coordinator = data["id"]
                print("End election (new coord: {})\n".format(self.coordinator))

            if data["type"] == Type['HEARTBEAT'].value:
                self.forwarding(self.id, Type['ACK'].value, address)

    def heartbeat(self):

        while True:

            time.sleep(TOTAL_DELAY)
            if self.coordinator == self.id:
                continue

            #self.wait_ack = True
            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nStarts Heartbeat\n".format(
                    self.ip, self.port, self.id))

            index = get_index(self.coordinator, self.nodes)
            info = self.nodes[index]
            dest = (info["ip"], info["port"])

            # create a new socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
            address = (self.ip, 0)
            s.bind(address)
            msg = create_msg(
                self.id, Type['HEARTBEAT'].value, address[1], address[0])
            s.settimeout(TOTAL_DELAY)
            s.sendto(msg, dest)

            try:
                data, address = s.recvfrom(BUFF_SIZE)
                data = eval(data.decode('utf-8'))
                if self.verbose:
                    self.logging.debug("Node: (ip:{} port:{} id:{})\nEnds Heartbeat\n".format(
                        self.ip, self.port, self.id))
            except socket.timeout:
                print("timeout for ACK\n")
                s.settimeout(None)
                s.close()
                self.start_election()

    def forwarding(self, id, type, dest):
        msg = create_msg(id, type, self.port, self.ip)
        self.socket.sendto(msg, dest)
