import json
import socket
from random import randint
import time
from math import floor


def delay(flag: bool, ub: int):
    if flag:
        delay = randint(0, floor(ub/2))
        time.sleep(delay)


def get_index(id: int, list: list) -> int:
    index = 0
    for item in list:
        if item.get('id') == id:
            return index
        index += 1
    return 0


def get_id(port: int, list: list) -> int:
    for item in list:
        if item.get('port') == port:
            return item.get('id')
    return 0


def create_msg(id: int, type: int, port: int, ip: str) -> bytes:

    msg = {'type': type, 'id': id, 'port': port, 'ip': ip}
    msg = json.dumps(msg)
    msg = str(msg).encode('utf-8')
    return msg


def create_socket(ip: str) -> socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (ip, 0)
    sock.bind(address)
    return sock
