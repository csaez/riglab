from setuptools import setup, find_packages

config = {
    "name": "riglab",
    "description": "Rigging framework.",
    "author": "Cesar Saez",
    "author_email": "hi@cesarsaez.me",
    "url": "http://www.github.com/csaez/riglab",
    "version": "0.1.0",
    "install_requires": [],
    "setup_requires": [],
    "packages": find_packages(exclude=['ez_setup', 'examples', 'tests'])}

setup(**config)
