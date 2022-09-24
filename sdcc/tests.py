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
from register.src.constants import SOCKET_TIMEOUT


class Tests:

    """
    The following tests are executed:
    - Test A: a generic node fails
    - Test B: coordinator fails
    - Test C: both generic and coordinator node fails
    """

    def __init__(self, nodes: int, algorithm: bool):
        self.num_nodes = nodes
        self.verbose = True
        self.nodes = []

        self.utils = Utils()
        self.logging = self.utils.set_logging()

        thread_register = Thread(target=self.generate_register)
        thread_register.daemon = True
        thread_register.start()

        time.sleep(SOCKET_TIMEOUT/4)

        for _ in range(self.num_nodes):
            process = Process(target=self.utils.generate_node,
                              args=(self.verbose, algorithm, True))
            process.daemon = True
            process.start()

        thread_register.join()

        self.logging.debug("================= Test =================\n"
                           "[Generated {} nodes]\n[More Details]: {}\n"
                           "========================================\n".format(
                               len(self.nodes), self.nodes))

    def test_a(self):

        time.sleep(HEARTBEAT_TIME * 3)

        index = randint(0, self.num_nodes - 2)
        port = self.nodes[index]["port"]
        self.utils.kill_node(port)

        time.sleep(HEARTBEAT_TIME * 3)

        self.utils.terminate(port, self.nodes)
        self.logging.debug("====== Test A finished =====\n")

    def test_b(self):

        time.sleep(HEARTBEAT_TIME * 3)

        port = self.nodes[-1]["port"]
        self.utils.kill_node(port)

        time.sleep(HEARTBEAT_TIME * 3)

        self.utils.terminate(port, self.nodes)
        self.logging.debug("====== Test B finished =====\n")

    def test_c(self):

        time.sleep(HEARTBEAT_TIME * 3)

        port = self.nodes[-1]["port"]
        self.utils.kill_node(port)

        index = randint(0, self.num_nodes - 2)
        port = self.nodes[index]["port"]
        self.utils.kill_node(port)

        time.sleep(HEARTBEAT_TIME * 3)

        self.utils.terminate(port, self.nodes)
        self.logging.debug("====== Test C finished =====\n")

    def generate_register(self):
        register = Register(self.verbose, "./config.json", True)
        register.receive()
        register.send()
        self.nodes = register.get_list()


class Utils:

    def __init__(self):
        pass

    def generate_node(self, verbose: bool, algo: bool, delay: bool):
        node = Node(verbose, algo, "./config.json", delay)
        node.start()

    def kill_node(self, port: int):
        for proc in process_iter():
            for conns in proc.connections(kind='inet'):
                if conns.laddr.port == port:
                    proc.send_signal(SIGINT)

    def terminate(self, port: int, nodes: list):
        for index in range(len(nodes) - 1):
            p = nodes[index]["port"]
            if p == port:
                continue
            self.kill_node(p)

    def set_logging(self) -> logging:
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(levelname)s] %(asctime)s\n%(message)s",
            datefmt='%b-%d-%y %I:%M:%S'
        )
        return logging
