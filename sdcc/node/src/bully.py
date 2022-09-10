from .algorithm import *


class Bully(Algorithm):

    def __init__(self, ip, port, id, nodes, socket, verbose):

        self.checked_nodes = 0
        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose)

    def start_election(self):
        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{}))\nStarts Election\n".format(
                self.ip, self.port, self.id))

        self.participant = True
        index = get_index(self.id, self.nodes) + 1

        # if current node is not the one with the greatest id
        if index != len(self.nodes):

            self.coordinator = -1
            self.checked_nodes = len(self.nodes) - index
            ack_nodes = self.checked_nodes

            for node in range(index, len(self.nodes)):
                ip = self.nodes[node]["ip"]
                port = self.nodes[node]["port"]
                dest = (ip, port)

                Algorithm.forwarding(
                    self, self.id, Type['ELECTION'].value, dest)

            timeout = time.time() + TOTAL_DELAY
            while (time.time() < timeout):
                # if the node receives (at least one) acks, will not be the coordinator
                # ACK pkt = END pkt
                if self.checked_nodes != ack_nodes:
                    self.participant = False
                    return

        # case in which the current node does not receive acks
        self.coordinator = self.id
        self.participant = False
        self.announce_election()

    def announce_election(self):

        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{}))\nSend Election messages\n".format(
                self.ip, self.id, self.id))

        for node in range(len(self.nodes) - 1):
            dest = (self.nodes[node]["ip"], self.nodes[node]["port"])
            Algorithm.forwarding(
                self, self.id, Type['END_ELECT'].value, dest)

    def end_election(self, data):
        id = data["id"]
        self.participant = False
        if id < self.coordinator:
            Algorithm.forwarding(
                self, self.coordinator, Type['END_ELECT'].value, (data["ip"], data["port"]))
            self.checked_nodes -= 1
            return

        self.checked_nodes = 0
        self.coordinator = data["id"]
        print("End election (new coord: {})\n".format(self.coordinator))

    def election_msg(self, data):
        id = get_id(data["port"], self.nodes)
        if id < self.id:
            Algorithm.forwarding(
                self, self.id, Type['END_ELECT'].value, (data["ip"], data["port"]))
            if self.participant == False:
                self.start_election()
