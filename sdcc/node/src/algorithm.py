from enum import Enum
import socket
import time
import signal as sign
import readchar
import sys
from . import helpers as help
from .constants import TOTAL_DELAY, BUFF_SIZE, HEARTBEAT_TIME
from abc import ABC, abstractmethod
from threading import Thread, Lock


class Type(Enum):
    ELECTION = 0
    END_ELECT = 1
    ACK = 2
    HEARTBEAT = 3
    REGISTER = 4


class Algorithm(ABC):

    def __init__(self, ip, port, id, nodes, socket, verbose):

        self.verbose = verbose
        self.ip = ip
        self.port = port
        self.id = id
        self.nodes = nodes
        self.socket = socket
        self.coordinator = -1
        self.lock = Lock()

        sign.signal(sign.SIGINT, self.handler)

        self.logging = help.set_logging()
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
    def end_election(self):
        pass

    @abstractmethod
    def election_msg(self):
        pass

    @abstractmethod
    def forwarding(self):
        pass

    def listening(self):

        while True:

            data, addr = self.socket.recvfrom(BUFF_SIZE)
            data = eval(data.decode('utf-8'))

            if self.verbose:
                help.print_log_rx(self.logging, (self.ip, self.port),
                                  addr, self.id, data)

            if data["type"] == Type['HEARTBEAT'].value:
                msg = help.create_msg(
                    self.id, Type['ACK'].value, self.port, self.ip)
                if self.verbose:
                    help.print_log_tx(self.logging, addr,
                                      (self.ip, self.port), self.id, eval(msg.decode('utf-8')))

                self.socket.sendto(msg, addr)
                continue

            type = {Type['ELECTION'].value: self.election_msg,
                    Type['END_ELECT'].value: self.end_election
                    }

            type[data["type"]](data)

    def crash(self, socket):
        socket.settimeout(None)
        # remove the last node (a.k.a coordinator)
        self.nodes.pop()
        self.lock.release()
        self.start_election()

    def heartbeat(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
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
                help.print_log_tx(self.logging, dest,
                                  (self.ip, self.port), self.id, eval(msg.decode('utf-8')))

            s.sendto(msg, dest)
            s.settimeout(TOTAL_DELAY)
            try:
                data, addr = s.recvfrom(BUFF_SIZE)
                data = eval(data.decode('utf-8'))
                if self.verbose:
                    help.print_log_rx(self.logging, dest, addr, self.id, data)

                if data["type"] != Type["ACK"].value:
                    self.crash(s)
                else:
                    self.lock.release()

            except socket.timeout:
                self.crash(s)

    def handler(self, signum, frame):
        msg = " (Ctrl-c was pressed. Do you really want to exit? y/n) "
        print(msg, end="", flush=True)
        res = readchar.readchar()
        if res == 'y':
            print("")
            sys.exit(1)
        else:
            print("", end="\r", flush=True)
            print(" " * len(msg), end="", flush=True)  # clear the printed line
            print("    ", end="\r", flush=True)
