from random import randint

from .constants import HEARTBEAT_TIME
from . import helpers as help
from .algorithm import Algorithm, Type
from . import verbose as verb
import sys
import time
import socket


class Ring(Algorithm):

    """
    The algorithm of Chang and Roberts [1979] is suitable for a collection of processes
    arranged in a logical ring. Each process has a communication channel
    to the next process in the ring, and all messages are sent clockwise around the ring.

    Types of messages exchanged:
        - Election = Election
        - Elected = End
    """

    def __init__(self, ip: str, port: int, id: int, nodes: list, socket: socket, verbose: bool, delay: bool, algo: bool):

        Algorithm.__init__(self, ip, port, id, nodes,
                           socket, verbose, delay, algo)

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

    # process receives an elected message
    def end_msg(self, data: dict):
        self.lock.acquire()
        if self.coordinator == self.id:
            self.lock.release()
            return

        self.participant = False
        self.coordinator = data["id"]
        self.forwarding(data["id"], Type['END'])
        self.lock.release()

    def election_msg(self, data: dict):

        self.lock.acquire()

        # compares the identifier in the message with its own
        current_id = data["id"]

        # current node becomes the coordinator
        if current_id == self.id:
            self.participant = False
            self.coordinator = self.id
            self.forwarding(current_id, Type['END'])
            self.lock.release()
            return

        elif current_id < self.id:
            if self.participant == False:
                # substitutes its own identifier in the message
                # and forwards it
                current_id = self.id
            else:
                self.lock.release()
                return

        # If the arrived identifier is greater,
        # it forwards the message to its neighbour
        self.participant = True
        self.forwarding(current_id, Type['ELECTION'])
        self.lock.release()

    def forwarding(self, id: int, type: Type):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, 0))

        if self.delay:
            delay = randint(0, HEARTBEAT_TIME*2)
            time.sleep(delay)

        index = help.get_index(self.id, self.nodes) + 1
        if index >= len(self.nodes):
            index = 0
        node = self.nodes[index]
        dest = (node["ip"], node["port"])

        msg = help.create_msg(id, type.value, self.port, self.ip)

        try:
            sock.connect(dest)
        except:
            self.nodes.pop(index)
            if len(self.nodes) == 1:
                sock.close()
                return
            self.forwarding(id, type)
            sock.close()
            return

        if self.verbose:
            verb.print_log_tx(self.logging, dest, (self.ip, self.port),
                              self.id, eval(msg.decode('utf-8')))

        sock.send(msg)
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

   # useless method needed in the bully alg.
    def answer_msg(self):
        pass
