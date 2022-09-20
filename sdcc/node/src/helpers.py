import json


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


def create_msg(id: int, type: int, port: int, ip: str) -> dict:

    msg = {'type': type, 'id': id, 'port': port, 'ip': ip}
    msg = json.dumps(msg)
    msg = str(msg).encode('utf-8')
    return msg
