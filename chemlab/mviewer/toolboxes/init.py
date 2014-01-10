__builtins__['viewer'] = viewer
viewer.ipython.app.shell.run_line_magic('load_ext', 'autoreload')
viewer.ipython.app.shell.run_line_magic('autoreload', '2')

from core import *
from select_ import * # underscore prevent shadowing the stdlib select
from display import *
from orderpar import *
from art import *

