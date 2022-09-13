from . import helpers as help
from .algorithm import Algorithm, Type


class Ring(Algorithm):

    def __init__(self, ip, port, id, nodes, socket, verbose):

        Algorithm.__init__(self, ip, port, id, nodes, socket, verbose)

    def start_election(self):

        # current node does not know if is the one with the greatest id
        # as difference in Bully alg.
        self.lock.acquire()
        self.participant = True
        self.forwarding(self.id, Type['ELECTION'])
        self.lock.release()

    def end_election(self, data):
        self.lock.acquire()
        if self.coordinator == self.id:
            return

        self.participant = False
        self.coordinator = data["id"]
        self.forwarding(data["id"], Type['END_ELECT'])
        self.lock.release()

    def election_msg(self, data):

        current_id = data["id"]
        self.lock.acquire()
        if current_id == self.id:
            self.participant = False
            self.coordinator = self.id
            self.forwarding(current_id, Type['END_ELECT'])
            self.lock.release()
            return

        elif current_id < self.id:

            if self.participant == False:
                self.participant = True
                current_id = self.id
                self.forwarding(
                    current_id, Type['ELECTION'])

        elif current_id > self.id:
            self.participant = True
            self.forwarding(
                current_id, Type['ELECTION'])

        # elif current_id < self.id and self.participant == False:
        #     current_id = self.id

        # self.participant = True
        # self.forwarding(current_id, Type['ELECTION'])
        # self.lock.release()

    def forwarding(self, id, type):
        index = help.get_index(self.id, self.nodes) + 1
        if index >= len(self.nodes):
            index = 0
        dest = (self.nodes[index]["ip"], self.nodes[index]["port"])
        msg = help.create_msg(id, type.value, self.port, self.ip)
        if self.verbose:
            help.print_log_tx(self.logging, dest, (self.ip, self.port),
                              self.id, eval(msg.decode('utf-8')))
        self.socket.sendto(msg, dest)
