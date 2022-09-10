import time
import threading as thr
import socket

from .algorithm import *


class Bully(Algorithm):

    def __init__(self, ip, port, id, nodes, socket, verbose):

        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose)
        self.ack_nodes = []
        self.number_initial_nodes = 0
        self.ack = False

        info = self.nodes[len(self.nodes) - 1]
        if info["id"] == self.id:
            self.coordinator = self.id
            self.announcing()
        else:
            self.waiting()

        # thread is listening for msg
        thread = thr.Thread(target=self.listening)
        thread.start()

        Algorithm.heartbeat(self)

    # sends a coordinator message to all
    # processes with lower identifiers

    def announcing(self):

        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{}))\nSend Election messages\n".format(
                self.ip, self.id, self.id))

        for node in range(len(self.nodes) - 1):
            dest = (self.nodes[node]["ip"], self.nodes[node]["port"])
            Algorithm.forwarding(
                self, self.socket, self.id, Type['END_ELECT'].value, dest, (self.ip, self.port))

    def waiting(self):

        self.socket.settimeout(TOTAL_DELAY)
        while True:
            try:
                data, addr = self.socket.recvfrom(BUFF_SIZE)
                data = eval(data.decode('utf-8'))
                if data["type"] == Type['END_ELECT'].value:
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
            Algorithm.forwarding(
                self, self.socket, self.id, Type['ELECTION'].value, dest, (self.ip, self.port))

        # in listening for a while
        timeout = time.time() + TOTAL_DELAY
        while time.time() < timeout:
            continue

        # if node do not received ack, will be the coordinator
        if self.number_initial_nodes == len(self.ack_nodes):
            self.announcing()
            self.coordinator = self.id
            print("End election (new coord: {})\n".format(self.coordinator))

    def election_msg(self, address):
        id = get_id(address[1], self.nodes)
        if id < self.id:
            Algorithm.forwarding(
                self, self.socket, self.id, Type['END_ELECT'].value, address, (self.ip, self.port))
            if self.participant == False:
                self.participant = True
                self.start_election()

    def listening(self):

        while True:

            data, address = self.socket.recvfrom(BUFF_SIZE)
            data = eval(data.decode('utf-8'))

            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nSender: (ip:{} port:{})\nMessage: {}\n".format(
                    self.ip, self.port, self.id, address[0], address[1], data))

            if data["type"] == Type['ELECTION'].value:
                self.election_msg(address)

            if data["type"] == Type['END_ELECT'].value:
                self.ack_nodes = []
                self.participant = False
                self.coordinator = data["id"]
                print("End election (new coord: {})\n".format(self.coordinator))

            if data["type"] == Type['HEARTBEAT'].value:
                Algorithm.forwarding(
                    self, self.socket, self.id, Type['ACK'].value, address, (self.ip, self.port))
