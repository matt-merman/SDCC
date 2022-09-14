from . import helpers as help
from .algorithm import Algorithm, Type
import sys


class Ring(Algorithm):

    """
    The algorithm of Chang and Roberts [1979] is suitable for a collection of processes
    arranged in a logical ring. Each process has a communication channel
    to the next process in the ring, and all messages are sent clockwise around the ring.

    Types of messages:
        - Election = Election
        - Elected = End
    """

    def __init__(self, ip, port, id, nodes, socket, verbose):

        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose)

    # useless method needed in the bully alg.
    def answer_msg(self):
        pass

    def start_election(self):

        self.lock.acquire()

        # check if current node is the last one
        if (len(self.nodes) == 1):
            self.socket.close()
            sys.exit(1)

        # a node marks itself as a participant, placing its identifier
        # in an election message and sending it to its clockwise neighbour
        self.participant = True
        self.forwarding(self.id, Type['ELECTION'])
        self.lock.release()

    def end_msg(self, data):
        self.lock.acquire()
        if self.coordinator == self.id:
            self.lock.release()
            return

        self.participant = False
        self.coordinator = data["id"]
        self.forwarding(data["id"], Type['END'])
        self.lock.release()

    def election_msg(self, data):

        self.lock.acquire()
        current_id = data["id"]
        if current_id == self.id:
            self.participant = False
            self.coordinator = self.id
            self.forwarding(current_id, Type['END'])
            self.lock.release()
            return

        elif current_id < self.id:
            if self.participant == False:
                current_id = self.id
            else:
                self.lock.release()
                return

        self.participant = True
        self.forwarding(current_id, Type['ELECTION'])
        self.lock.release()

    def forwarding(self, id, type):
        index = help.get_index(self.id, self.nodes) + 1
        if index >= len(self.nodes):
            index = 0
        node = self.nodes[index]
        dest = (node["ip"], node["port"])

        msg = help.create_msg(id, type.value, self.port, self.ip)

        if self.verbose:
            help.print_log_tx(self.logging, dest, (self.ip, self.port),
                              self.id, eval(msg.decode('utf-8')))

        self.socket.sendto(msg, dest)
