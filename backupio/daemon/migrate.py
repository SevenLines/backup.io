from backupio.daemon import db
from backupio.daemon.models import Backup

Backup.metadata.create_all(db.engine)