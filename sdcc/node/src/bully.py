from . import helpers as help
from .algorithm import Algorithm, Type
from .constants import TOTAL_DELAY
import time


class Bully(Algorithm):

    def __init__(self, ip, port, id, nodes, socket, verbose):

        self.checked_nodes = 0
        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose)

    def start_election(self):

        self.participant = True
        index = help.get_index(self.id, self.nodes) + 1

        # if current node is not the one with the greatest id
        if index != len(self.nodes):

            self.coordinator = -1
            self.checked_nodes = len(self.nodes) - index
            ack_nodes = self.checked_nodes

            for node in range(index, len(self.nodes)):
                self.forwarding(self.nodes[node], self.id, Type['ELECTION'])

            timeout = time.time() + TOTAL_DELAY
            while (time.time() < timeout):
                # if the node receives (at least one) acks, will not be the coordinator
                # ACK pkt = END pkt
                if self.checked_nodes != ack_nodes:
                    self.participant = False
                    return

        # case in which the current node does not receive acks
        self.coordinator = self.id
        self.participant = False
        # announce the node election
        for node in range(len(self.nodes) - 1):
            self.forwarding(self.nodes[node], self.id, Type['END_ELECT'])

    def end_election(self, msg):
        id = msg["id"]
        if id < self.coordinator:
            self.forwarding(msg, self.coordinator, Type['END_ELECT'])
            self.checked_nodes -= 1
            return

        self.checked_nodes = 0
        self.coordinator = msg["id"]

    def election_msg(self, msg):
        id = help.get_id(msg["port"], self.nodes)
        if id < self.id:
            self.forwarding(msg, self.id, Type['END_ELECT'])
            if self.participant == False:
                self.start_election()

    def forwarding(self, node, id, type):
        ip = node["ip"]
        port = node["port"]
        dest = (ip, port)
        msg = help.create_msg(id, type.value, self.port, self.ip)
        if self.verbose:
            help.print_log_tx(self.logging, dest, (self.ip, self.port),
                              self.id, eval(msg.decode('utf-8')))
        self.socket.sendto(msg, dest)
