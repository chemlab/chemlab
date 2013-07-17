from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, Extension
from Cython.Distutils import build_ext
import numpy as np

ext_modules = [Extension('chemlab.libs.ckdtree', ['chemlab/libs/ckdtree.pyx']),
               Extension('chemlab.utils.celllinkedlist',
                         ['chemlab/utils/celllinkedlist.pyx']),
               Extension('chemlab.utils.cdist',
                         ['chemlab/utils/cdist.pyx']),
               Extension('chemlab.molsim.rdf', 
                         ['chemlab/molsim/rdf.pyx']),
               Extension('chemlab.graphics.renderers.utils', 
                         ['chemlab/graphics/renderers/utils.pyx']),
               Extension('chemlab.libs.pyxdr._xdrfile',
                          ["chemlab/libs/pyxdr/xdrfile.c",
                           "chemlab/libs/pyxdr/xdrfile_trr.c", 
                           "chemlab/libs/pyxdr/xdrfile_xtc.c",
                           "chemlab/libs/pyxdr/_xdrfile.pyx"],
                            include_dirs=['./chemlab/libs/'])]

setup(
    name = "chemlab",
    version = "0.3",
    packages = find_packages(),
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules,
    include_dirs = [np.get_include()],
    package_data = {'': ['distribute_setup.py', '*.rst', '*.txt'],
                    'chemlab.graphics.renderers.shaders': ['*.vert', '*.frag'],
                    'chemlab.graphics.postprocessing.shaders': ['*.vert', '*.frag'],
                    'chemlab.resources' : ["*"],
                    'chemlab.db.localdb.data' : ['*'],
                    'chemlab.db.localdb.molecule' : ['*'],
                    'chemlab.core.spacegroup': ['*']},
    
    author = "Gabriele Lanaro",
    scripts = ['scripts/chemlab'],
    zip_safe = False,
    
    
    author_email = "gabriele.lanaro@gmail.com",
    description = "The python chemistry library you were waiting for",
    long_description = '''
    chemlab is a python library and a set of utilities built to ease the
    life of the computational chemist. It takes inspiration from other
    python scientific library such as numpy scipy and matplotlib, and aims
    to bring a consistent and simple API by following the python
    guidelines.

    Computational and theoretical chemistry is a huge
    field, and providing a program that encompasses all aspects of it is an
    impossible task. The spirit of chemlab is to provide a common ground
    from where you can build specific programs. For this reason it
    includes an easily extendable molecular viewer and flexible data
    structures field-independent.
    ''',
    classifiers = ['Intended Audience :: Science/Research',
                   'Topic :: Scientific/Engineering :: Chemistry',
                   'Topic :: Scientific/Engineering :: Visualization',
                   'Topic :: Scientific/Engineering :: Physics',
                   'Topic :: Multimedia :: Graphics :: Viewers',
                   'Programming Language :: Python :: 2.7'],
    license = "GPL3",
    keywords = "chemistry molecular_viewer",
    url = "https://chemlab.github.com/chemlab"
)
