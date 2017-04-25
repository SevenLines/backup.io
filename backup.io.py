import argparse
import json
import os

from terminaltables import AsciiTable

from core.task import BackupTask

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="path to json file which used for task")
    parser.add_argument("action", help="action to execute, available: backup, restore, list")
    parser.add_argument("-n", "--count",
                        help="count of items to show, use only with list, pass 0 to show all",
                        type=int,
                        default=5)
    parser.add_argument("-f", "--force-full",
                        help="force full backup, used with backup action only",
                        action='store_true')
    parser.add_argument("-r", "--restore-name",
                        help="name of backup to restore, use only with restore action",
                        )
    parser.add_argument("-t", "--restore-to",
                        help="path to where restore backup, use only with restore action",
                        default="/")
    parser.add_argument("-d", "--dereference",
                        help="don't archive symlinks; archive the files they point to, the same as tar  -h flag",
                        action='store_true')

    args = parser.parse_args()

    with open(args.config) as f:
        data = json.load(f)

    task = BackupTask().from_data(data)
    action = args.action
    if action == 'backup':
        task.backup(args.force_full, args.dereference)
    elif action == 'list':
        count = args.count
        table_data = [
            ['DATE', 'NAME', 'PATH', 'IS_FULL']
        ]
        files = task.get_backup_files()

        if count:
            files = files[:count]

        for file in reversed(files):
            table_data.append([
                file['date'].isoformat(),
                os.path.basename(file['path']),
                file['path'],
                file['is_full']
            ])
        table = AsciiTable(table_data)
        print(table.table)
    elif action == 'restore':
        if not args.restore_name:
            print("please specify backup to restore with --restore-name (-r) argument")
            exit(1)
        task.restore(args.restore_name, args.restore_to)
