import json
import socket
import struct

from backupio.daemon.helpers import json_serializer, json_date_hook


class ServerClient(object):
    socket = None
    host = ""
    port = ""

    def __init__(self) -> None:
        self.socket = socket.socket()

    async def connect(self, host, port):
        self.socket.connect((host, port))
        self.host = host
        self.port = port

    async def close(self):
        self.socket.close()

    def reconnect(self):
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

    async def login(self, user, password):
        return self.send({
            "action": "login",
            "parameters": {
                'user': user,
                'password': password
            }
        })

    async def get_backups(self):
        return self.send({
            "action": "list_backups",
        })

    async def get_list_backup_tasks(self):
        return self.send({
            'action': 'list_backup_tasks',
        })

    async def add_backup_task(self,
                        name,
                        output_folder,
                        input_elements=None,
                        execute_before_scripts=None,
                        execute_after_scripts=None,
                        exclude=None,
                        keep_n_last_full_backups=0,
                        full_backup_every=0):

        if exclude is None:
            exclude = []
        if execute_after_scripts is None:
            execute_after_scripts = []
        if execute_before_scripts is None:
            execute_before_scripts = []
        if input_elements is None:
            input_elements = []

        return self.send({
            'action': 'add_backup_task',
            'parameters': {
                'name': name,
                'output_folder': output_folder,
                'keep_n_last_full_backups': keep_n_last_full_backups,
                'full_backup_every': full_backup_every,
                'input_elements': input_elements,
                'execute_before_scripts': execute_before_scripts,
                'execute_after_scripts': execute_after_scripts,
                'exclude': exclude,
            }
        })

    async def backup(self, force_full=False):
        return self.send({
            "action": 'backup',
            'parameters': {
                'force_full': force_full
            }
        })