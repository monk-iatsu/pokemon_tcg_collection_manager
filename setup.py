from setuptools import setup, find_packages
import os

VERSION = '0.1.2'
DESCRIPTION = 'Log Pokemon cards'
LONG_DESCRIPTION = 'a module to log and manage a pokemon card collection'

# Setting up
setup(
    name="pokemonCardLogger",
    version=VERSION,
    author="rosejustin601 (Justin Rose)",
    author_email="rosejustin601@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'pokemon', 'card', 'tcg'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English"
    ]
)
