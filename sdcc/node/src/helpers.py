import json


def get_index(id, list):
    index = 0
    for item in list:
        if item.get('id') == id:
            return index
        index += 1
    return 0


def get_id(port, list):
    for item in list:
        if item.get('port') == port:
            return item.get('id')
    return 0


def create_msg(id, type, port, ip):

    msg = {'type': type, 'id': id, 'port': port, 'ip': ip}
    msg = json.dumps(msg)
    msg = str(msg).encode('utf-8')
    return msg
