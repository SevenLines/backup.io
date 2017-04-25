backup.io
=========

python tar-based backup utility

Creating backup set config file
-------------------------------

Create config.json file:

    {
      "name": "tic_tac_toe", // backup set name
      "full_backup_every": 7,  // create full backup on each 7-th backup archive
      "keep_n_last_full_backups": 4, // keep 4 last full backup archives
      "output_folder": "backups", // the output folde in which create backups archive
      "execute_before_scripts": [
        "pg_dump -d irgid -c -f /home/user/backup.io/test/dump.sql" // scripts to execute before taring starts
      ],
      "execute_after_scripts": [
        "rm /home/user/backup.io/test/dump.sql" // scripts to execute before taring starts
      ],
      "exclude": [ // list of files, or dirs to exclude from set
        "/home/user/backup.io/test/exclude.me"
      ],
      "input_elements": [
        "/home/user/backup.io/test" // files or folders to add to archive
      ]
    }

now you can use this config to create backups

Create backup
-------------

    python backup.io.py config.json backup

This command creates in "backups" folder next files

    tictactoe_20170425210935.full.tar.gz  # actual full backup archive
    tictactoe_20170425210935.snar  # snar file to track incremental backups

run command ones more:

    python backup.io.py config.json backup

now you backups dir has this files:

    tictactoe_20170425210935.full.tar.gz  # actual full backup archive
    tictactoe_20170425210935.snar  # snar file to track incremental backups
    tictactoe_20170425211012.i.tar.gz  # incremental backup

you can force create full backup by passing -f flag

    python backup.io.py config.json backup -f

Setting keep_n_last_full_backups=4 means that your backup dir always have no more than 4 full backups.
I.e. if you have 4 *.full.tar.gz files in backups files, and you call backup action, then the oldest full backup
will be deleted with all it's descendants incremental archives.

List backups sets
-----------------

Run

    python backup.io.py config.json list

it will return table of last 5 backups

+---------------------+----------------------------------------+-----------------------------------------------------------+---------+
| DATE                | NAME                                   | PATH                                                      | IS_FULL |
+---------------------+----------------------------------------+-----------------------------------------------------------+---------+
| 2017-04-25T21:09:35 | tic_tac_toe_20170425210935.full.tar.gz | /home/user/backups/tic_tac_toe_20170425210935.full.tar.gz | True    |
| 2017-04-25T21:19:47 | tic_tac_toe_20170425211947.i.tar.gz    | /home/user/backups/tic_tac_toe_20170425211947.i.tar.gz    | False   |
+---------------------+-----------------------------------------+----------------------------------------------------------+---------+


you can list 10 last or all backups by passing flag n with 10 and 0 respectively:

    python backup.io.py config.json list -n 10
    python backup.io.py config.json list -n 0


Restore backup set
------------------

To restore backup archive use restore action with backups archive name:

    python backup.io.py config.json restore -r tic_tac_toe_20170425211947.i.tar.gz

it will try to restore archive with all absolute paths to /
that's mean that if you backup /home/user/test directory, restore action restore that directory exactly

You can specify dir to restore by passing -t flag

    python backup.io.py config.json restore -r tic_tac_toe_20170425211947.i.tar.gz -t /home/user/output

Restore backup set without config file
--------------------------------------
It's possible to restore without config file by passing path to folder with backups instead path to json config:

    python backup.io.py /home/user/backups restore -r tic_tac_toe_20170425211947.i.tar.gz

utility tries to find out name of set, and archives in it
You can also list backups in folder with list command:

    python backup.io.py /home/user/backups list