from daemon import db
from daemon.models import Backup

Backup.metadata.create_all(db.engine)