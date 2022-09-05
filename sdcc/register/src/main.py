import socket
import sys
import json
import time
from threading import Thread


class Register:

    def __init__(self):

        self.ip = "192.168.1.7"
        self.port = 12345
        self.log = []
        self.address_nodes = []
        self.reception_window = 5  # seconds

    def receive(self, socket):

        while True:
            # recvfrom() is blocking
            data, address = socket.recvfrom(4096)
            # add data to a list
            # need a mutex to write on it
            self.address_nodes.append(address)
            self.log.append(data.decode('utf-8'))

    # open a connection
    def listen(self):

        # Create a UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind the socket to the port
        server_address = (self.ip, self.port)
        s.bind(server_address)

        thread = Thread(target=self.receive, args=(s, ))
        thread.start()

        timeout_start = time.time() + self.reception_window
        # in listening for a while
        while time.time() < timeout_start:
            continue

        # need to kill thread
        # ...
        # perhaps I'll need to use process

        self.send_log(s)

    def send_log(self, s):

        # need to generate the IDs for all nodes
        # ...

        # send list to all nodes
        for i in range(len(self.address_nodes)):

            address = self.address_nodes[i]
            s.sendto(str(self.log).encode('utf-8'), address)

        s.close()
