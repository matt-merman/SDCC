from signal import SIGINT
from psutil import process_iter
from register.src.main import Register
from node.src.main import Node
from threading import Thread
import logging
import time
from multiprocessing import Process
from node.src.constants import HEARTBEAT_TIME
from random import randint


class Tests:

    """
    The following tests are executed:
    - TEST A: a generic node fails 
    - TEST B: coordinator fails
    - TEST C: both generic node and coordinator fail
    """

    def __init__(self, n: int, algorithm: bool):
        self.num_nodes = n
        self.verbose = True
        self.nodes = []
        self.logging = self.set_logging()
        self.algorithm = algorithm
        self.num_proc = 0

        thread_register = Thread(target=self.generate_register)
        thread_register.daemon = True
        thread_register.start()

        for _ in range(self.num_nodes):
            process = Process(target=self.generate_node)
            process.daemon = True
            process.start()

        thread_register.join()

        self.logging.debug("Generated {} nodes\nMore Details {}\n".format(
            self.num_nodes, self.nodes))

    def generate_node(self):
        node = Node(self.verbose, self.algorithm, "./node/config.json")
        node.start()

    def generate_register(self):
        register = Register(self.verbose, "./register/config.json")
        register.receive()
        self.nodes = register.get_list()
        register.send()

    def kill_node(self, port):
        for proc in process_iter():
            for conns in proc.connections(kind='inet'):
                if conns.laddr.port == port:
                    proc.send_signal(SIGINT)

    def test_a(self):

        index = randint(0, self.num_nodes - 2)
        port = self.nodes[index]["port"]
        self.kill_node(port)

        # keep running the application for a while
        timeout = time.time() + HEARTBEAT_TIME*5
        while time.time() < timeout:
            continue

        for index in range(self.num_nodes - 1):
            p = self.nodes[index]["port"]
            if p == port:
                continue
            self.kill_node(p)

        self.logging.debug("Test A finished\n")

    def test_b(self):

        port = self.nodes[-1]["port"]
        self.kill_node(port)

        # keep running the application for a while
        timeout = time.time() + HEARTBEAT_TIME*5
        while time.time() < timeout:
            continue

        for index in range(self.num_nodes - 1):
            p = self.nodes[index]["port"]
            if p == port:
                continue
            self.kill_node(p)

        self.logging.debug("Test B finished\n")

    def test_c(self):

        port = self.nodes[-1]["port"]
        self.kill_node(port)

        index = randint(0, self.num_nodes - 2)
        port = self.nodes[index]["port"]
        self.kill_node(port)

        # keep running the application for a while
        timeout = time.time() + HEARTBEAT_TIME*5
        while time.time() < timeout:
            continue

        for index in range(self.num_nodes - 2):
            p = self.nodes[index]["port"]
            if p == port:
                continue
            self.kill_node(p)

        self.logging.debug("Test C finished\n")

    def set_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(levelname)s] %(asctime)s\n%(message)s",
            datefmt='%b-%d-%y %I:%M:%S'
        )
        return logging
