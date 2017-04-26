from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Integer, Text, String

Base = declarative_base()


class Backup(Base):
    __tablename__ = 'backups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    output_folder = Column(String)
    keep_n_last_full_backups = Column(Integer)
    full_backup_every = Column(Integer)
    input_elements = Column(Text)
    execute_before_scripts = Column(Text)
    execute_after_scripts = Column(Text)
    exclude = Column(Text)
