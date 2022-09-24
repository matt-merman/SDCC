from enum import Enum
import socket
import time
import signal as sign
import sys
from . import helpers as help
from .constants import TOTAL_DELAY, BUFF_SIZE, HEARTBEAT_TIME
from abc import ABC, abstractmethod
from threading import Thread, Lock
from . import verbose as verb


class Type(Enum):

    """
    Class contains message types exchanged in Bully and Ring-based algorithm. 
    """

    ELECTION = 0
    END = 1
    ANSWER = 2
    HEARTBEAT = 3
    REGISTER = 4
    ACK = 5


class Algorithm(ABC):

    """
    Parent class for Bully and Ring classes. 
    """

    def __init__(self, ip: str, port: int, id: int,
                 nodes: list, socket: socket, verbose: bool, delay: bool, algo: bool):

        self.ip = ip
        self.port = port
        self.id = id
        self.nodes = nodes
        self.socket = socket
        self.algo = algo

        self.coordinator = -1
        self.lock = Lock()

        # boolean params passed by command line
        self.delay = delay
        self.verbose = verbose

        sign.signal(sign.SIGINT, self.handler)

        self.logging = verb.set_logging()

        # by default a node does not participate to election
        self.participant = False

        thread = Thread(target=self.listening)
        thread.daemon = True
        thread.start()

        self.start_election()
        Algorithm.heartbeat(self)

    @abstractmethod
    def start_election(self):
        pass

    @abstractmethod
    def end_msg(self, msg: dict):
        pass

    @abstractmethod
    def answer_msg(self):
        pass

    @abstractmethod
    def election_msg(self, msg: dict):
        pass

    @abstractmethod
    def forwarding(self):
        pass

    def listening(self):

        while True:

            conn, addr = self.socket.accept()
            data = conn.recv(BUFF_SIZE)
            data = eval(data.decode('utf-8'))

            verb.print_log_rx(self.verbose, self.logging, (self.ip, self.port),
                              addr, self.id, data)

            if data["type"] == Type['HEARTBEAT'].value:

                help.delay(self.delay, HEARTBEAT_TIME*3)

                msg = help.create_msg(
                    self.id, Type['ACK'].value, self.port, self.ip)

                verb.print_log_tx(self.verbose, self.logging, addr,
                                  (self.ip, self.port), self.id, eval(msg.decode('utf-8')))

                conn.send(msg)
                continue

            elif data["type"] == Type['ANSWER'].value:
                self.answer_msg()
                conn.close()
                continue

            func = {Type['ELECTION'].value: self.election_msg,
                    Type['END'].value: self.end_msg
                    }

            func[data["type"]](data)

    # method to manage a leaders' crash
    def crash(self):
        # if using ring alg. remove the last node (a.k.a. leader)
        if self.algo == False:
            self.nodes.pop()

        self.lock.release()
        self.start_election()

    def heartbeat(self):

        while True:

            hb_sock = help.create_socket(self.ip)
            address = hb_sock.getsockname()

            time.sleep(HEARTBEAT_TIME)
            self.lock.acquire()
            # do not heartbeat the leader if current node is running an election
            # or if is the leader
            if self.participant or (self.coordinator == self.id):
                self.lock.release()
                continue

            index = help.get_index(self.coordinator, self.nodes)
            info = self.nodes[index]

            msg = help.create_msg(
                self.id, Type['HEARTBEAT'].value, address[1], address[0])

            try:
                dest = (info["ip"], info["port"])
                hb_sock.connect(dest)
                verb.print_log_tx(self.verbose, self.logging, dest,
                                  (self.ip, self.port), self.id, eval(msg.decode('utf-8')))
                hb_sock.send(msg)
                self.receive_ack(hb_sock, dest, TOTAL_DELAY)

            # current leader suffers a crash
            except:
                hb_sock.close()
                self.crash()

    def receive_ack(self, sock: socket, dest: tuple, waiting: int):

        # need to calculate the starting time to provide
        # a residual time to use as timeout when invalid packet is received
        start = round(time.time())
        sock.settimeout(waiting)

        try:
            data = sock.recv(BUFF_SIZE)
            msg = eval(data.decode('utf-8'))

            # expected packet received (i.e., with current leaders' id and ack type)
            if (msg["id"] == self.coordinator) and (msg["type"] == Type["ACK"].value):
                self.lock.release()

            # invalid packet received (e.g., a delayed ack by the previous leader)
            else:
                stop = round(time.time())
                waiting -= (stop-start)
                self.receive_ack(sock, dest, waiting)

            addr = (msg["ip"], msg["port"])
            verb.print_log_rx(self.verbose, self.logging,
                              dest, addr, self.id, msg)
            sock.close()

        except socket.timeout:
            sock.close()
            self.crash()

    def handler(self, signum: int, frame):
        self.logging.debug("[Node]: (ip:{} port:{} id:{})\n[Killed]\n".format(
            self.ip, self.port, self.id))
        self.socket.close()
        sys.exit(1)
