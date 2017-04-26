import asyncio

from daemon.server import ServerClientProtocol
from core.task import BackupTask


def main():
    task = BackupTask()
    task.full_backup_every = 3
    task.keep_n_last_full_backups = 2

    task.name = "tic_tac_toe"
    task.output_folder = "backups"
    task.execute_before_scripts = [
        "pg_dump -d irgid -c -f /home/m/PycharmProjects/backup.io/test/dump.sql"
    ]
    task.input_elements = [
        "/home/m/PycharmProjects/backup.io/test",
    ]
    task.execute_after_scripts = [
        'rm /home/m/PycharmProjects/backup.io/test/dump.sql'
    ]
    task.exclude = [
        # "/home/m/PycharmProjects/irgid/irgid/node_modules",
        # "/home/m/PycharmProjects/irgid/irgid/media",
        # "/home/m/PycharmProjects/irgid/irgid/.git",
        # "/home/m/PycharmProjects/irgid/irgid/templates/static/.webassets-cache"
    ]

    # task.restore('tic_tac_toe_20170424033240.i.tar.gz',
    #              restore_to="/home/m/PycharmProjects/backup.io/output")
    task.backup()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    coro = loop.create_server(ServerClientProtocol, port=9997)
    server = loop.run_until_complete(coro)

    for socket in server.sockets:
        print("serving on {}".format(socket.getsockname()))

    loop.run_forever()