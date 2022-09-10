from .algorithm import *


class Ring(Algorithm):

    def __init__(self, ip, port, id, nodes, socket, verbose):

        self.fail = False
        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose)

    def start_election(self):
        if self.verbose:
            self.logging.debug("Node: (ip:{} port:{} id:{})\nStarts election\n".format(
                self.ip, self.port, self.id))

        self.participant = True

        id = self.nodes[len(self.nodes) - self.number_crash]["id"]
        if (self.id == id) and (self.number_crash > 1):
            self.fail = True
        dest = get_dest(self.fail, self.id, self.nodes)

        Algorithm.forwarding(
            self, self.socket, self.id, Type['ELECTION'].value, dest, (self.ip, self.port))

    def end_election(self, data):
        if self.coordinator != self.id:
            self.participant = False
            self.coordinator = data["id"]
            dest = get_dest(self.fail, self.id, self.nodes)
            Algorithm.forwarding(
                self, self.socket, data["id"], Type['END_ELECT'].value, dest, (self.ip, self.id))

    def election_msg(self, data):

        id = data["id"]
        dest = get_dest(self.fail, self.id, self.nodes)

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
