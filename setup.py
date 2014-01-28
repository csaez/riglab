from setuptools import setup, find_packages

config = {
    "name": "riglab",
    "description": "Rigging framework for Softimage.",
    "author": "Cesar Saez",
    "author_email": "cesarte@gmail.com",
    "url": "http://www.github.com/csaez/riglab",
    "version": "0.1.0",
    "install_requires": ["wishlib>=0.2.0", "rigicon", "naming"],
    "setup_requires": [],
    "packages": find_packages(exclude=['ez_setup', 'examples', 'tests']),
    "scripts": [],
    "entry_points": {},
}

setup(**config)
