"""dSNES project configuration."""
# Copyright 2017 Adrian Chan
# Licensed under GPLv3

from setuptools import setup, find_packages


packages = find_packages()
print("Packages are:\n{}".format(packages))

setup(
    name='dSNES',

    version='0.1.0',

    description='General-purpose SNES disassembler',

    url='https://github.com/achan1989/dSNES',

    author='Adrian Chan',

    license='GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.5',
    ],

    packages=packages,

    # Use this specific version of contoml because of monkey-patch bug fix.
    install_requires=['contoml == 0.32']
)