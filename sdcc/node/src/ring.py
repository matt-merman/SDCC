from .constants import HEARTBEAT_TIME, LISTENING
from . import helpers as help
from .algorithm import Algorithm, Type
from . import verbose as verb
import sys
import os
import socket
import time


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

        #time.sleep(5)
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
    def end_msg(self, msg: dict):
        self.lock.acquire()
        if self.coordinator == self.id:
            self.lock.release()
            return

        self.participant = False
        self.coordinator = msg["id"]
        self.forwarding(msg["id"], Type['END'])
        self.lock.release()

    def election_msg(self, msg: dict):

        self.lock.acquire()

        # compares the identifier in the message with its own
        current_id = msg["id"]

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

        sock = help.create_socket(self.ip)
        help.delay(self.delay, LISTENING)

        index = help.get_index(self.id, self.nodes) + 1
        if index >= len(self.nodes):
            index = 0

        node = self.nodes[index]
        msg = help.create_msg(id, type.value, self.port, self.ip)

        try:
            dest = (node["ip"], node["port"])
            sock.connect(dest)
            verb.print_log_tx(self.verbose, self.logging, dest, (self.ip, self.port),
                              self.id, eval(msg.decode('utf-8')))
            sock.send(msg)
            sock.close()

        except ConnectionRefusedError:
            self.nodes.pop(index)
            sock.close()
            if len(self.nodes) != 1:
                self.forwarding(id, type)
            else:
                self.socket.close()
                os._exit(1)

    def answer_msg(self):
        # useless method needed in the bully alg.
        pass
