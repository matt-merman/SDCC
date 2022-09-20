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
from random import randint


class Type(Enum):
    ELECTION = 0
    END = 1
    ANSWER = 2
    HEARTBEAT = 3
    REGISTER = 4
    ACK = 5


class Algorithm(ABC):

    def __init__(self, ip: str, port: int, id: int,
                 nodes: list, socket: socket, verbose: bool, delay: bool):

        self.verbose = verbose
        self.ip = ip
        self.port = port
        self.id = id
        self.nodes = nodes
        self.socket = socket
        self.coordinator = -1
        self.lock = Lock()
        self.delay = delay

        sign.signal(sign.SIGINT, self.handler)

        self.logging = verb.set_logging()
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

            data, addr = self.socket.recvfrom(BUFF_SIZE)
            data = eval(data.decode('utf-8'))

            if self.verbose:
                verb.print_log_rx(self.logging, (self.ip, self.port),
                                  addr, self.id, data)

            if data["type"] == Type['HEARTBEAT'].value:

                if self.delay:
                    delay = randint(0, HEARTBEAT_TIME*2)
                    time.sleep(delay)

                msg = help.create_msg(
                    self.id, Type['ACK'].value, self.port, self.ip)

                if self.verbose:
                    verb.print_log_tx(self.logging, addr,
                                      (self.ip, self.port), self.id, eval(msg.decode('utf-8')))

                self.socket.sendto(msg, addr)
                continue

            elif data["type"] == Type['ANSWER'].value:
                self.answer_msg()
                continue

            func = {Type['ELECTION'].value: self.election_msg,
                    Type['END'].value: self.end_msg

                    }

            func[data["type"]](data)

    def crash(self, socket: socket):
        socket.settimeout(None)
        # remove the last node (a.k.a coordinator)
        self.nodes.pop()
        self.lock.release()
        self.start_election()

    def heartbeat(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address = (self.ip, 0)
        s.bind(address)
        address = s.getsockname()

        while True:

            time.sleep(HEARTBEAT_TIME)

            self.lock.acquire()
            if self.participant or (self.coordinator == self.id):
                self.lock.release()
                continue

            index = help.get_index(self.coordinator, self.nodes)
            info = self.nodes[index]
            dest = (info["ip"], info["port"])

            msg = help.create_msg(
                self.id, Type['HEARTBEAT'].value, address[1], address[0])

            if self.verbose:
                verb.print_log_tx(self.logging, dest,
                                  (self.ip, self.port), self.id, eval(msg.decode('utf-8')))

            s.sendto(msg, dest)
            self.receive(s, dest, TOTAL_DELAY)

    def receive(self, sock: socket, dest: tuple, waiting: int):

        start = round(time.time())
        sock.settimeout(waiting)

        try:
            data, addr = sock.recvfrom(BUFF_SIZE)
            data = eval(data.decode('utf-8'))
            if self.verbose:
                verb.print_log_rx(self.logging, dest, addr, self.id, data)

            if data["id"] == self.coordinator and data["type"] == Type["ACK"].value:
                self.lock.release()

            else:
                sock.settimeout(None)
                stop = round(time.time())
                self.receive(sock, dest, waiting - (stop-start))

        except socket.timeout:
            self.crash(sock)

    def handler(self, signum: int, frame):
        self.logging.debug("[Node]: (ip:{} port:{} id:{})\nKilled\n".format(
            self.ip, self.port, self.id))
        sys.exit(1)
