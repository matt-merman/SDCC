import json
import time


class Ring():

    def __init__(self, ip, port, id, nodes, socket):
        self.ip = ip
        self.port = port
        self.id = id
        self.nodes = nodes
        self.socket = socket

        self.coordinator_id = None

        # initially, every process is marked as a non-participant in an election
        self.participant = False

    def forwarding(self, data):
        if self.id == 3:
            index = 0
        else:
            index = self.id

        info = json.loads(self.nodes[index])
        ip_dest = info["ip"]
        port_dest = info["port"]

        msg = self.create_msg(data["id"], 1)
        time.sleep(3)
        self.socket.sendto(msg, (ip_dest, port_dest))

    def listening(self):

        while(1):

            data, _ = self.socket.recvfrom(4096)
            data = eval(data.decode('utf-8'))
            print("Node {id: %d} received election msg {id: %d}" %
                  (self.id, data["id"]))

            if self.coordinator_id == self.id:
                continue

            # election's end
            if data["id"] == self.id:
                self.participant = False
                self.coordinator_id = self.id
                print("Election's end")
                # sent elected msg to all nodes
                for i in range(len(self.nodes)):
                    info = json.loads(self.nodes[i])
                    ip_dest = info["ip"]
                    port_dest = info["port"]
                    id_dest = info["id"]
                    if id_dest == self.id:
                        continue

                    info = self.create_msg(self.id, 0)
                    self.socket.sendto(info, (ip_dest, port_dest))

                continue

            elif data["flag"] == 0:
                self.participant = False
                self.coordinator_id = data["id"]
                self.forwarding(data)

            elif data["id"] > self.id:
                self.participant = True
                self.forwarding(data)

            elif self.participant == False and data["id"] < self.id:
                self.participant = True
                data["id"] = self.id
                self.forwarding(data)

    def starting(self):

        print("Node {id: %d} started election" % (self.id, ))
        self.participant = True
        msg = self.create_msg(self.id, 1)

        print("Election msg: {id: %d}" % (eval(msg.decode('utf-8'))["id"], ))

        if self.id == 3:
            index = 0
        else:
            index = self.id

        info = json.loads(self.nodes[index])

        ip_dest = info["ip"]
        port_dest = info["port"]

        self.socket.sendto(msg, (ip_dest, port_dest))

        # receiving
        # ack = s.recvfrom(4096)

        self.listening()

    def create_msg(self, id, flag):

        info = json.dumps({'flag': flag, 'id': id})
        return str(info).encode('utf-8')
