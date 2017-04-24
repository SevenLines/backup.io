import json
import socket
import struct

from daemon.helpers import json_serializer, json_date_hook


class ServerClient(object):
    socket = None
    host = ""
    port = ""

    def __init__(self) -> None:
        self.socket = socket.socket()

    def connect(self, host, port):
        self.socket.connect((host, port))
        self.host = host
        self.port = port

    def close(self):
        self.socket.close()

    def reconnect(self):
        self.socket.close()
        self.connect(host=self.host, port=self.port)

    def send(self, data):
        self.socket.send(json.dumps(data, default=json_serializer).encode())
        response = self._recv_msg()
        return json.loads(response.decode(), object_hook=json_date_hook)

    def _recv_msg(self):
        # Read message length and unpack it into an integer
        raw_msglen = self._recvall(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self._recvall(msglen)

    def _recvall(self, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while len(data) < n:
            packet = self.socket.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def login(self, user, password):
        return self.send({
            "action": "login",
            "parameters": {
                'user': user,
                'password': password
            }
        })

    def get_backups(self):
        return self.send({
            "action": "list_backups",
        })

    def backup(self, force_full=False):
        return self.send({
            "action": 'backup',
            'parameters': {
                'force_full': force_full
            }
        })