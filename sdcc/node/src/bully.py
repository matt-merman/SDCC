from . import helpers as help
from .algorithm import Algorithm, Type
from .constants import TOTAL_DELAY, HEARTBEAT_TIME
import time
import socket
from random import randint
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

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, 0))

        self.lock.acquire()

        index = help.get_index(self.id, self.nodes) + 1
        self.participant = True

        # node with a lower identifier can begin an election
        if index != len(self.nodes):

            self.coordinator = -1
            self.checked_nodes = len(self.nodes) - index
            ack_nodes = self.checked_nodes

            # election messages are sent to those processes that have a higher identifier
            for node in range(index, len(self.nodes)):
                try:
                    sock.connect(
                        (self.nodes[node]["ip"], self.nodes[node]["port"]))
                except:
                    continue
                self.forwarding(self.nodes[node],
                                self.id, Type['ELECTION'], sock)

            self.lock.release()

            # awaiting answer messages in response
            timeout = time.time() + TOTAL_DELAY
            while (time.time() < timeout):
                self.lock.acquire()
                # an answer message has been received
                if self.checked_nodes != ack_nodes:
                    self.lock.release()
                    # waits a further period for a coordinator message
                    self.further_waiting()
                    return
                self.lock.release()

            self.lock.acquire()

        # node with the highest identifier,
        # or who does not receive answers
        # elects itself as the coordinator
        self.coordinator = self.id
        self.participant = False

        # send a coordinator message to all processes
        # with lower identifiers
        for node in range(len(self.nodes) - 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.ip, 0))
            print(self.nodes[node])
            if node == (index - 1):
                continue
            try:
                sock.connect(
                    (self.nodes[node]["ip"], self.nodes[node]["port"]))
            except:
                print("here2\n")
                continue

            self.forwarding(self.nodes[node], self.id, Type['END'], sock)
            sock.close()

        self.lock.release()

    def answer_msg(self):
        self.lock.acquire()
        self.checked_nodes -= 1
        self.lock.release()

    # received a coordinator message
    def end_msg(self, msg: dict):

        print("here\n")

        self.lock.acquire()
        self.coordinator = msg["id"]
        self.coordinator_msg = True
        self.lock.release()

    def election_msg(self, msg: dict):
        self.lock.acquire()
        self.forwarding(msg, self.id, Type['ANSWER'], None)
        if self.participant == False:
            self.lock.release()
            self.start_election()
            return

        self.lock.release()

    def forwarding(self, node: dict, id: int, type: Type, conn: socket):

        if self.delay:
            delay = randint(0, HEARTBEAT_TIME*2)
            time.sleep(delay)

        ip = node["ip"]
        port = node["port"]
        dest = (ip, port)
        msg = help.create_msg(id, type.value, self.port, self.ip)
        if self.verbose:
            verb.print_log_tx(self.logging, dest, (self.ip, self.port),
                              self.id, eval(msg.decode('utf-8')))

        if conn == None:
            e_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            e_sock.bind((self.ip, 0))
            e_sock.connect(dest)
            e_sock.send(msg)
            e_sock.close
        else:
            conn.sendto(msg, dest)

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

        self.lock.acquire()
        self.participant = False
        self.lock.release()

        self.start_election()
