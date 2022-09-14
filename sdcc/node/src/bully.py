from . import helpers as help
from .algorithm import Algorithm, Type
from .constants import TOTAL_DELAY
import time
import sys


class Bully(Algorithm):

    """
    The bully algorithm [Garcia-Molina 1982] allows processes to crash
    during an election. It assumes that message delivery between processes is reliable and 
    that each process knows which processes have higher identifiers, and that it can
    communicate with all such processes.

    Types of messages:
        - Coordinator -> End
        - Election -> Election
        - Answer -> Answer
    """

    def __init__(self, ip, port, id, nodes, socket, verbose):

        self.checked_nodes = 0
        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose)

    def start_election(self):

        self.lock.acquire()

        # check if current node is the last one
        if (len(self.nodes) == 1):
            self.socket.close()
            sys.exit(1)

        index = help.get_index(self.id, self.nodes) + 1
        self.participant = True

        # node with a lower identifier can begin an election
        if index != len(self.nodes):

            self.coordinator = -1
            self.checked_nodes = len(self.nodes) - index
            ack_nodes = self.checked_nodes

            # send election messages to those processes that have a higher identifier
            for node in range(index, len(self.nodes)):
                self.forwarding(self.nodes[node], self.id, Type['ELECTION'])

            self.lock.release()

            # awaiting answer messages in response
            timeout = time.time() + TOTAL_DELAY
            while (time.time() < timeout):
                self.lock.acquire()
                if self.checked_nodes != ack_nodes:
                    self.participant = False
                    self.lock.release()
                    return

                self.lock.release()

            self.lock.acquire()

        # node with the highest identifier, or does not receive answers
        # elect itself as the coordinator
        self.coordinator = self.id
        self.participant = False

        # send a coordinator message to all processes
        for node in range(len(self.nodes) - 1):
            self.forwarding(self.nodes[node], self.id, Type['END'])

        self.lock.release()

    def answer_msg(self):
        self.lock.acquire()
        self.checked_nodes -= 1
        self.lock.release()

    def end_msg(self, msg):
        self.lock.acquire()
        self.coordinator = msg["id"]
        self.lock.release()

    def election_msg(self, msg):
        self.lock.acquire()
        self.forwarding(msg, self.id, Type['ANSWER'])
        if self.participant == False:
            self.lock.release()
            self.start_election()
            return

        self.lock.release()

    def forwarding(self, node, id, type):
        ip = node["ip"]
        port = node["port"]
        dest = (ip, port)
        msg = help.create_msg(id, type.value, self.port, self.ip)
        if self.verbose:
            help.print_log_tx(self.logging, dest, (self.ip, self.port),
                              self.id, eval(msg.decode('utf-8')))
        self.socket.sendto(msg, dest)
