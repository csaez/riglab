from setuptools import setup, find_packages

config = {
    "name": "riglab",
    "description": "Rigging framework for Softimage.",
    "author": "Cesar Saez",
    "author_email": "cesarte@gmail.com",
    "url": "https://www.github.com/csaez/riglab",
    "version": "0.1.0",
    "install_requires": ["nose", "wishlib>=0.1.4", "rigicon"],
    "setup_requires": ["nose>=1.0"],
    "packages": find_packages(exclude=['ez_setup', 'examples', 'tests']),
    "scripts": [],
    "entry_points": {"gui_scripts": ["namingeditor = riglab.naming.editor:main"]},
}

setup(**config)
