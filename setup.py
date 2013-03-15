from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name = "chemlab",
    version = "0.1",
    packages = find_packages(),
    package_data = {'': ['distribute_setup.py', '*.rst', '*.txt'],
                    'chemlab.graphics.renderers.shaders': ['*.vert', '*.frag'],
                    'chemlab.resources' : ["*"],
                    'chemlab.data' : ['*']},
    
    install_requires = ["numpy", "pyopengl", "pyside"],
    author = "Gabriele Lanaro",
    scripts = ['scripts/chemlab'],
    zip_safe = False,
    
    
    author_email = "gabriele.lanaro@gmail.com",
    description = "The python chemistry library you were waiting for",
    long_description = '''
    chemlab is a ptyhon library and a set of utilities built to ease the
    life of the computational chemist. It takes inspiration from other
    python scientific library such as numpy scipy and matplotlib, and aims
    to bring a consistent and simple API by following the python
    guidelines.

    This package is still in its early development, going forward to the
    first 0.1 release. Computational and theoretical chemistry is a huge
    field, and providing a program that encompasses all aspect of it is an
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
