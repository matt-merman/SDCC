from .algorithm import *


class Ring(Algorithm):

    def __init__(self, ip, port, id, nodes, socket, verbose):

        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose)

    def start_election(self):
        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{})\nStarts election\n".format(
                self.ip, self.port, self.id))

        # current node does not know if is the one with the greatest id
        # as difference in Bully alg.
        dest = get_dest(self.id, self.nodes)
        self.participant = True
        Algorithm.forwarding(self, self.id, Type['ELECTION'].value, dest)

    def end_election(self, data):
        if self.coordinator == self.id:
            return
        self.participant = False
        self.coordinator = data["id"]

        dest = get_dest(self.id, self.nodes)
        Algorithm.forwarding(
            self, data["id"], Type['END_ELECT'].value, dest)

    def election_msg(self, data):

        current_id = data["id"]
        dest = get_dest(self.id, self.nodes)
        if current_id == self.id:
            self.participant = False
            self.coordinator = self.id
            if self.verbose:
                self.logging.debug("Node: (ip:{} port:{} id:{})\nElected as Coordinator\n".format(
                    self.ip, self.port, self.id))

            Algorithm.forwarding(
                self, current_id, Type['END_ELECT'].value, dest)
            return

        elif current_id < self.id:

            if self.participant == False:
                self.participant = True
                current_id = self.id
                Algorithm.forwarding(
                    self, current_id, Type['ELECTION'].value, dest)

        elif current_id > self.id:
            self.participant = True
            Algorithm.forwarding(
                self, current_id, Type['ELECTION'].value, dest)
