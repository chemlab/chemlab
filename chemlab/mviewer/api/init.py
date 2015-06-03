__builtins__['viewer'] = viewer
viewer.ipython.run_line_magic('load_ext', 'autoreload')
viewer.ipython.run_line_magic('autoreload', '2')

from .core import *
from .selections import *
from .display import *
from .appeareance import *

# Ok, now we should add some code that import the thing
import os, sys

CHEMPATH = os.path.expanduser('~/.chemlab')
sys.path.insert(0, CHEMPATH)

if os.path.exists(os.path.join(CHEMPATH, 'scripts', '__init__.py')):
    from scripts import *
else:
    print('Create the {} file to put initialization code'.
          format(os.path.join(CHEMPATH,'scripts', '__init__.py')))
