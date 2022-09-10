import threading as thr

from .algorithm import *
from .constants import *

from .verbose import *
from .helpers import *


class Ring(Algorithm):

    def __init__(self, ip, port, id, nodes, socket, verbose):

        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose)
        thread = thr.Thread(target=self.listening)
        thread.start()
        self.start_election()
        Algorithm.heartbeat(self)

    def end(self, data):
        if self.coordinator != self.id:
            self.participant = False
            self.coordinator = data["id"]
            dest = get_dest(self.id, self.nodes)
            Algorithm.forwarding(
                self, self.socket, data["id"], Type['END_ELECT'].value, dest, (self.ip, self.id))
        print(self.coordinator)

    def election_msg(self, data):

        id = data["id"]
        dest = get_dest(self.id, self.nodes)

        if id < self.id:

            if self.participant == False:
                data["id"] = self.id
                self.participant = True
            else:
                return

        elif id == self.id:
            self.participant = False
            self.coordinator = self.id
            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nElected as Coordinator\n".format(
                    self.ip, self.port, self.id))

            Algorithm.forwarding(
                self, self.socket, data["id"], Type['END_ELECT'].value, dest, (self.ip, self.id))
            return

        Algorithm.forwarding(
            self, self.socket, data["id"], Type['ELECTION'].value, dest, (self.ip, self.id))

    def listening(self):

        while True:

            data, address = self.socket.recvfrom(BUFF_SIZE)
            data = eval(data.decode('utf-8'))

            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nSender: (ip:{} port:{})\nMessage: {}\n".format(
                    self.ip, self.port, self.id, address[0], address[1], data))

            type_one = Type['ELECTION'].value
            type_two = Type['END_ELECT'].value

            if data["type"] == Type['HEARTBEAT'].value:
                Algorithm.forwarding(
                    self, self.socket, self.id, Type['ACK'].value, address, (self.ip, self.port))
                continue

            type = {type_one: self.election_msg,
                    type_two: self.end
                    }

            type[data["type"]](data)

    def start_election(self):
        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{})\nStarts election\n".format(
                self.ip, self.port, self.id))

        self.participant = True
        dest = get_dest(self.id, self.nodes)
        Algorithm.forwarding(
            self, self.socket, self.id, Type['ELECTION'].value, dest, (self.ip, self.id))
