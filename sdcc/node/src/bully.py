from . import helpers as help
from .algorithm import Algorithm, Type
from .constants import DEFAULT_ID, TOTAL_DELAY, HEARTBEAT_TIME
import time
import socket
from . import verbose as verb


class Bully(Algorithm):

    """
    The bully algorithm [Garcia-Molina 1982] assumes that
    each process knows which processes have higher identifiers, and that it can
    communicate with all such processes.

    Types of messages exchanged:
        - Coordinator -> End
        - Election -> Election
        - Answer -> Answer
    """

    def __init__(self, ip: str, port: int, id: int, nodes: list, socket: socket, verbose: bool, delay: bool, algo: bool):

        self.checked_nodes = 0
        self.coordinator_msg = False
        Algorithm.__init__(self, ip, port, id, nodes,
                           socket, verbose, delay, algo)

    def start_election(self):

        sock = help.create_socket(self.ip)
        self.lock.acquire()
        index = help.get_index(self.id, self.nodes) + 1
        self.participant = True

        # node with a lower identifier can begin an election
        if (index != len(self.nodes)) and (self.low_id_node(sock, index) == 0):
            sock.close()
            return

        # node with the highest identifier,
        # or who does not receive answers
        # elects itself as the coordinator
        self.coordinator = self.id
        self.participant = False
        sock.close()

        # send a coordinator message to all processes
        # with lower identifiers
        for node in range(len(self.nodes) - 1):
            sock = help.create_socket(self.ip)
            if node == (index - 1):
                continue
            try:
                sock.connect(
                    (self.nodes[node]["ip"], self.nodes[node]["port"]))
                self.forwarding(self.nodes[node], self.id, Type['END'], sock)
                sock.close()
            except ConnectionRefusedError:
                continue

        self.lock.release()

    def low_id_node(self, sock: socket, index: int) -> int:

        self.coordinator = DEFAULT_ID
        self.checked_nodes = len(self.nodes) - index
        ack_nodes = self.checked_nodes

        # election messages are sent to those processes that have a higher identifier
        for node in range(index, len(self.nodes)):
            try:
                sock.connect(
                    (self.nodes[node]["ip"], self.nodes[node]["port"]))
            # if a node is no more available contact the next one
            except ConnectionRefusedError:
                continue

            self.forwarding(self.nodes[node],
                            self.id, Type['ELECTION'], sock)

        sock.close()
        self.lock.release()
        # awaiting answer messages in response
        timeout = time.time() + TOTAL_DELAY
        while (time.time() < timeout):
            self.lock.acquire()
            # an answer message has been received
            if self.checked_nodes != ack_nodes:
                self.lock.release()
                # wait a further period for a coordinator message
                self.further_waiting()
                return 0
            self.lock.release()

        self.lock.acquire()
        return 1

    # further waiting time for the coordinator message
    def further_waiting(self):
        timeout = time.time() + TOTAL_DELAY
        while (time.time() < timeout):
            self.lock.acquire()
            if self.coordinator_msg == True:
                self.participant = False
                self.coordinator_msg = False
                self.lock.release()
                return
            self.lock.release()

        # if the coordinator message has not been received
        # node starts a new election
        self.lock.acquire()
        self.participant = False
        self.lock.release()
        self.start_election()

    def answer_msg(self):
        self.lock.acquire()
        self.checked_nodes -= 1
        self.lock.release()

    # received a coordinator message
    def end_msg(self, msg: dict):
        self.lock.acquire()
        self.coordinator = msg["id"]
        self.coordinator_msg = True
        self.lock.release()

    def election_msg(self, msg: dict):

        self.lock.acquire()

        sock = help.create_socket(self.ip)
        sock.connect((msg["ip"], msg["port"]))
        self.forwarding(msg, self.id, Type['ANSWER'], sock)
        sock.close()

        if self.participant == False:
            self.lock.release()
            self.start_election()
            return

        self.lock.release()

    def forwarding(self, node: dict, id: int, type: Type, conn: socket):

        help.delay(self.delay, HEARTBEAT_TIME)
        dest = (node["ip"], node["port"])
        msg = help.create_msg(id, type.value, self.port, self.ip)
        verb.print_log_tx(self.verbose, self.logging, dest,
                          (self.ip, self.port), self.id, eval(msg.decode('utf-8')))
        conn.send(msg)
