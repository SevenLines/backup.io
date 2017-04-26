import asyncio
import json
import struct

from sqlalchemy.orm import sessionmaker

from core.task import TestBackupTask
from daemon import db
from daemon.helpers import json_serializer, json_date_hook
from daemon.models import Backup

clients = []

Session = sessionmaker()


def login_required(func):
    def wrapper(inst, *args, **kwargs):
        if inst.is_authenticated:
            return func(inst, *args, **kwargs)
        else:
            raise Exception("Not permitted. Login first")

    return wrapper


class ServerClientProtocol(asyncio.Protocol):
    is_authenticated = False
    transport = None
    backup_tasks = []

    def login(self, user, password):
        if user == "admin" and password == "bavaga5a7r=he8retruthabrama5aV":
            self.is_authenticated = True

    @login_required
    def list_backups(self):
        return TestBackupTask().get_backup_files()

    @login_required
    def backup(self, force_full=False):
        return TestBackupTask().backup(force_full=force_full)

    @login_required
    def list_backup_tasks(self):
        tasks = db.session.query(Backup).all()
        return tasks

    @login_required
    def add_backup_task(self, **data):
        db.session.add(Backup(**data))

    def connection_lost(self, exc):
        clients.remove(self)
        print("connection close")

    def connection_made(self, transport):
        super().connection_made(transport)

        self.transport = transport
        clients.append(self)

        print("connection made")

    def send(self, data):
        data_bytes = json.dumps(data, default=json_serializer).encode()
        data_bytes = struct.pack(">I", len(data_bytes)) + data_bytes
        self.transport.write(data_bytes)

    def data_received(self, data: bytes):
        super().data_received(data)
        data = json.loads(data.decode(), object_hook=json_date_hook)

        try:
            action = {
                'login': self.login,
                'list_backups': self.list_backups,
                'backup': self.backup,
                'list_backup_tasks': self.list_backup_tasks,
                'add_backup_task': self.add_backup_task,
            }.get(data['action'], lambda *args, **kwargs: None)
            result = action(**data.get('parameters', {}))
            self.send({
                'data': result,
                'success': True
            })
        except Exception as ex:
            self.send({
                'error': str(ex),
                'success': False
            })
            raise
