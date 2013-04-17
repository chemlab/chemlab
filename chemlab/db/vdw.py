import os
from .local import LocalDB

curdir = os.path.dirname(__file__) + '/localdb'
db = LocalDB(curdir)

vdw_dict = db.get("data", "vdwdict")
