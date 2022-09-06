from enum import Enum
import time
import threading as thr
import logging
from .helpers import *

# type: 0 - starting election, 1 - ending election, 2 - heartbeat, 3 - ACK

HEARTBEAT_TIME = 5


class Type(Enum):
    STARTING = 0
    ENDING = 1
    HEARTBEAT = 2
    ACK = 3


class Ring():

    def __init__(self, ip, port, id, nodes, socket):

        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(levelname)s] %(asctime)s\n%(message)s",
            datefmt='%b-%d-%y %I:%M:%S'
        )

        self.ip = ip
        self.port = port
        self.id = id
        self.nodes = nodes
        self.socket = socket
        self.coordinator = False

        # initially, every process is marked as a non-participant in an election
        self.participant = True
        self.ack = False

        logging.debug("[INFO]-(ip:{} port:{} id:{})".format(
            self.ip, self.port, self.id))

        # thread is listening for msg
        time.sleep(10)
        thread = thr.Thread(target=self.starting)
        thread.start()

        # thread is sending heartbeat msg
        thread = thr.Thread(target=self.heartbeat)
        thread.start()

    def end(self, data):
        if self.coordinator != self.id:
            self.participant = False
            self.coordinator = data["id"]
            dest = get_dest(self.id, self.nodes)
            self.forwarding(data, Type['ENDING'].value, dest)
        return

    def ack(self, data):
        ip_dest = data["ip"]
        port_dest = data["port"]
        dest = (ip_dest, port_dest)
        self.forwarding(self.id, Type['ACK'].value, dest)
        print("Node {id: %d} received heartbeat msg" % (self.id, ))
        return

    def receiving(self, data):

        id = data["id"]
        self.participant = True
        dest = get_dest(self.id, self.nodes)

        if id < self.id:

            if self.participant == False:
                data["id"] = self.id
            else:
                self.participant = False
                return

        elif id == self.id:
            self.participant = False
            self.coordinator = self.id
            print("Election's end")
            self.forwarding(data["id"], Type['ENDING'].value, dest)
            return

        self.forwarding(data["id"], Type['STARTING'].value, dest)
        return

    def starting(self):

        print("Node {id: %d} started election" % (self.id, ))
        dest = get_dest(self.id, self.nodes)
        self.forwarding(self.id, Type['STARTING'].value, dest)

        while(1):

            data, _ = self.socket.recvfrom(4096)
            data = eval(data.decode('utf-8'))
            print("Node {id: %d} received msg" %
                  (self.id))

            type_one = Type['STARTING'].value
            type_two = Type['ENDING'].value
            type_three = Type['ACK'].value
            type_four = Type['HEARTBEAT'].value

            if data["type"] == type_four:
                self.ack = True
                continue

            type = {type_one: self.receiving,
                    type_two: self.end,
                    type_three: self.ack,
                    }

            type[data["type"]](data)

    def heartbeat(self):

        while(True):

            time.sleep(HEARTBEAT_TIME)

            if self.participant or (self.coordinator == self.id):
                continue

            print("Node {id: %d} starts heartbeat" % (self.id, ))

            index = get_index(self.coordinator, self.nodes)
            info = self.nodes[index]
            dest = (info["ip"], info["port"])
            self.forwarding(self.id, Type['HEARTBEAT'].value, dest)

            # waiting util it receives the ack
            while not self.ack:
                None

            print("Node {id: %d} ends heartbeat" % (self.id, ))

    def forwarding(self, id, type, dest):
        msg = create_msg(id, type, 0, self.ip)
        self.socket.sendto(msg, dest)