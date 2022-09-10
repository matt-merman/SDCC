from .algorithm import *


class Bully(Algorithm):

    def __init__(self, ip, port, id, nodes, socket, verbose):

        self.ack_nodes = []
        self.number_initial_nodes = 0
        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose)

    def start_election(self):
        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{}))\nStart Election\n".format(
                self.ip, self.port, self.id))

        self.participant = True
        index = get_index(self.id, self.nodes)
        index += 1

        # case in which the current node owns the greatest id
        if index == len(self.nodes):
            self.announce_election()
            self.coordinator = self.id
            print("End election (new coord: {})\n".format(self.coordinator))
            return

        self.number_initial_nodes = len(self.nodes) - index

        for node in range(index, len(self.nodes)):
            dest = (self.nodes[node]["ip"], self.nodes[node]["port"])
            self.ack_nodes.append(self.nodes[node]["id"])
            Algorithm.forwarding(
                self, self.socket, self.id, Type['ELECTION'].value, dest, (self.ip, self.port))

        # in listening for a while
        timeout = time.time() + TOTAL_DELAY
        while time.time() < timeout:
            continue

        # if the node do not receive acks, will be the coordinator
        if self.number_initial_nodes == len(self.ack_nodes):
            self.announce_election()
            self.coordinator = self.id
            print("End election (new coord: {})\n".format(self.coordinator))

    def announce_election(self):

        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{}))\nSend Election messages\n".format(
                self.ip, self.id, self.id))

        for node in range(len(self.nodes) - 1):
            dest = (self.nodes[node]["ip"], self.nodes[node]["port"])
            Algorithm.forwarding(
                self, self.socket, self.id, Type['END_ELECT'].value, dest, (self.ip, self.port))

        self.participant = False

    def end_election(self, data):
        id = data["id"]
        if id < self.coordinator:
            Algorithm.forwarding(
                self, self.socket, self.coordinator, Type['END_ELECT'].value, (data["ip"], data["port"]), (self.ip, self.port))
            self.ack_nodes = []
            self.participant = False
            return

        self.ack_nodes = []
        self.participant = False
        self.coordinator = data["id"]
        print("End election (new coord: {})\n".format(self.coordinator))

    def election_msg(self, data):
        id = get_id(data["port"], self.nodes)
        if id < self.id:
            Algorithm.forwarding(
                self, self.socket, self.id, Type['END_ELECT'].value, (data["ip"], data["port"]), (self.ip, self.port))
            if self.participant == False:
                self.start_election()
