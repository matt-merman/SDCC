import json
import time
import threading as thr
import logging

# flag: 0 - starting election, 1 - ending election, 2 - heartbeat, 3 - ACK

HEARTBEAT_TIME = 5


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
        self.participant = False
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

    def forwarding(self, data, flag):
        index = self.find_index(self.id)
        index += 1
        if (index >= len(self.nodes)):
            index = 0

        info = self.nodes[index]
        ip_dest = info["ip"]
        port_dest = info["port"]

        msg = self.create_msg(data["id"], flag, 0)
        # time.sleep(3)
        self.socket.sendto(msg, (ip_dest, port_dest))

    def ending_msg(self, data):

        if self.coordinator != self.id:
            self.participant = False
            self.coordinator = data["id"]
            self.forwarding(data, 1)

        return

    def heartbeat_msg(self, data):
        ip_dest = 'localhost'
        port_dest = data["port"]

        msg = self.create_msg(self.id, 3, 0)
        self.socket.sendto(msg, (ip_dest, port_dest))
        print("Node {id: %d} received heartbeat msg" % (self.id, ))

        return

    def starting_msg(self, data):

        id = data["id"]

        if id > self.id:
            self.participant = True
            self.forwarding(data, 0)

        elif id == self.id:
            self.participant = False
            self.coordinator = self.id
            print("Election's end")
            self.forwarding(data, 1)

        elif id < self.id and self.participant == False:
            self.participant = True
            data["id"] = self.id
            self.forwarding(data, 0)

        return

    def listening(self):

        while(1):

            data, _ = self.socket.recvfrom(4096)
            data = eval(data.decode('utf-8'))
            print("Node {id: %d} received msg" %
                  (self.id))

            if data["flag"] == 3:
                self.ack = True
                continue

            flag = {0: self.starting_msg,
                    1: self.ending_msg,
                    2: self.heartbeat_msg,
                    }

            flag[data["flag"]](data)

    def starting(self):

        print("First Thread spawned!")

        print("Node {id: %d} started election" % (self.id, ))

        self.participant = True
        msg = self.create_msg(self.id, 0, 0)

        index = self.find_index(self.id)
        index += 1
        if (index >= len(self.nodes)):
            index = 0

        info = self.nodes[index]

        ip_dest = info["ip"]
        port_dest = info["port"]

        self.socket.sendto(msg, (ip_dest, port_dest))

        # receiving
        # ack = s.recvfrom(4096)

        self.listening()

    def heartbeat(self):

        print("Second Thread spawned!")

        while(1):

            time.sleep(HEARTBEAT_TIME)

            if self.participant or (self.coordinator == self.id):
                continue

            print("Node {id: %d} starts heartbeat" % (self.id, ))

            index = self.find_index(self.coordinator)

            info = self.nodes[index]
            ip_dest = info["ip"]
            port_dest = info["port"]

            msg = self.create_msg(self.id, 2, self.port)
            self.socket.sendto(msg, (ip_dest, port_dest))

            # waiting util it receives the ack
            while self.ack == False:
                None

            print("Node {id: %d} ends heartbeat" % (self.id, ))

    def find_index(self, id):
        position = 0
        for item in self.nodes:
            if item.get('id') == id:
                return position
            position += 1
        return 0

    def create_msg(self, id, flag, port):

        info = json.dumps({'flag': flag, 'id': id, 'port': port})
        return str(info).encode('utf-8')
