from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name = "chemlab",
    version = "0.1",
    packages = find_packages(),
    install_requires = ["pyglet", "numpy"],
    dependency_links = [
        "http://pyglet.googlecode.com/files/pyglet-1.1.4.tar.gz"
    ],
    author = "Gabriele Lanaro",
    author_email = "gabriele.lanaro@gmail.com",
    description = "Theoretical chemistry utilities for humans",
    license = "GPL2",
    keywords = "chemistry molecular_viewer",
    url = "https://github.com/chemlab/chemlab"
)
