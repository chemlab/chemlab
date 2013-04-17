import os
from .local import LocalDB
curdir = os.path.dirname(__file__) + '/localdb'
cdb = LocalDB(curdir)
