import os
import re
import shlex
import traceback
from datetime import datetime
from subprocess import run


class BackupTask(object):
    name = ""
    timestamp_format = "%Y%m%d%H%M%S"
    output_folder = "/tmp/"
    keep_n_last_full_backups = 0  # 0 mean keep all files
    full_backup_every = 0  # 0 mean every backup is full
    input_elements = []  # folder and files to
    execute_before_scripts = []  # scripts to execute before task starts
    execute_after_scripts = []  # scripts to execute after task complete
    exclude = []

    def __init__(self) -> None:
        super().__init__()

    def from_data(self, data):
        self.name = data['name']
        self.output_folder = data['output_folder']
        self.keep_n_last_full_backups = data['keep_n_last_full_backups']
        self.full_backup_every = data['full_backup_every']
        self.input_elements = data['input_elements']
        self.execute_before_scripts = data['execute_before_scripts']
        self.execute_after_scripts = data['execute_after_scripts']
        self.exclude = data['exclude']
        return self

    def from_dir(self, directory_path):
        self.output_folder = directory_path
        files = os.listdir(directory_path)
        if not files:
            raise Exception("directory is empty")

        # try to find name
        name = None
        for file in files:
            match = re.match(r"(\w+)_(\d+)\.(\w+)\.tar\.gz", file)
            if match:
                name = match.group(1)
                break
        if name is None:
            raise Exception("faile to get backupset name")

        self.name = name
        return self

    def _get_name(self, is_full=False, dt=datetime.now()):
        is_full_postfix = ".full" if is_full else ".i"
        name = self.name + "_" + dt.strftime(self.timestamp_format) + is_full_postfix + '.tar.gz'
        return shlex.quote(name)

    def _get_snar_file_name(self, dt=datetime.now()):
        name = self.name + "_" + dt.strftime(self.timestamp_format) + ".snar"
        return shlex.quote(os.path.join(self._get_output_folder(), name))

    def _get_exclude(self):
        for ex in self.exclude:
            yield shlex.quote("--exclude={}".format(ex))

    def _get_files(self):
        for item in self.input_elements:
            yield shlex.quote("{item}".format(item=item))

    def _get_output_folder(self):
        return shlex.quote(os.path.abspath(self.output_folder))

    def _parse_file_name(self, filename):
        template = re.compile(r"{name}_(\d+)\.(\w+)\.tar\.gz".format(name=self.name))
        match = template.match(filename)
        if match:
            try:
                timestamp = match.group(1)
                is_full = match.group(2) == 'full'
                date = datetime.strptime(timestamp, self.timestamp_format)
                return {
                    'path': os.path.join(self._get_output_folder(), filename),
                    'date': date,
                    'is_full': is_full,
                    'snar_path': self._get_snar_file_name(date) if is_full else "",
                }
            except Exception as ex:
                traceback.print_exc()
        return None

    def get_backup_files(self):
        files = []
        for file in os.listdir(self._get_output_folder()):
            file_info = self._parse_file_name(file)
            if file_info:
                files.append(file_info)
        files.sort(key=lambda x: x['date'])
        files.reverse()
        return files

    def _check_is_make_full(self):
        if self.full_backup_every <= 0:
            return True

        files = self.get_backup_files()
        index = 0
        for index, file in enumerate(files, 1):
            if file['is_full']:
                break

        return index == 0 or index >= self.full_backup_every

    def clean(self):
        if self.keep_n_last_full_backups <= 0:
            return

        full_counter = 0
        can_delete = False
        for index, backup in enumerate(self.get_backup_files()):
            if can_delete:
                os.remove(backup['path'])
                if backup['snar_path']:
                    os.remove(backup['snar_path'])
            else:
                if backup['is_full']:
                    full_counter += 1
                if full_counter == self.keep_n_last_full_backups:
                    can_delete = True

    def _get_snars_files(self):
        template = re.compile(r"{name}_(\d+)\.snar".format(name=self.name))
        files = []
        for file in os.listdir(self._get_output_folder()):
            match = template.match(file)
            if match:
                try:
                    timestamp = match.group(1)
                    date = datetime.strptime(timestamp, self.timestamp_format)
                    files.append({
                        'path': os.path.join(self._get_output_folder(), file),
                        'date': date,
                    })
                except Exception as ex:
                    traceback.print_exc()
        files.sort(key=lambda x: x['date'])
        files.reverse()
        return files

    def restore(self, filename, restore_to=None, strip_components=None):
        os.makedirs(restore_to, exist_ok=True)

        file_info = self._parse_file_name(filename)
        files = self.get_backup_files()
        backup_files_to_restore = []
        for file in files:
            if file['date'] <= file_info['date']:
                backup_files_to_restore.append(file)
                if file['is_full']:
                    break
        backup_files_to_restore.reverse()
        for file in backup_files_to_restore:
            cmd = shlex.split("tar --extract -G {restore_to} {strip_components} --file {file}".format(
                file=file['path'],
                restore_to="-C {}".format(restore_to) if restore_to else "",
                strip_components="--strip-components={}".format(
                    strip_components) if strip_components is not None else ""
            ))
            run(cmd)

    def backup(self, force_full=False, dereference=False):
        os.makedirs(self._get_output_folder(), exist_ok=True)

        for script in self.execute_before_scripts:
            run(shlex.split(script))

        dt = datetime.now()

        if self.input_elements:
            is_full = force_full or self._check_is_make_full()

            cmd = shlex.split(
                "tar -cpvzf {output_folder}/{name}".format(
                    output_folder=self._get_output_folder(),
                    name=self._get_name(is_full, dt),
                )
            )

            cmd += list(self._get_exclude())

            if is_full:
                cmd += ['-g', self._get_snar_file_name(dt)]
            else:
                snars = self._get_snars_files()
                snar = snars[0]['path'] if snars else self._get_snars_files()
                cmd += ['-g', snar]

            if dereference:
                cmd += ["-h", ]

            cmd += list(self._get_files())

            run(cmd)
        else:
            raise Exception("no files provided")

        for script in self.execute_after_scripts:
            run(shlex.split(script))

        self.clean()


