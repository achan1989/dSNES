"""dSNES project configuration."""

from setuptools import setup, find_packages


packages = find_packages()
print("Packages are:\n{}".format(packages))

setup(
    name='dSNES',

    version='0.1.0',

    description='General-purpose SNES disassembler',

    url='https://github.com/achan1989/dSNES',

    author='achan1989',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],

    packages=packages,

    install_requires=[]
)
