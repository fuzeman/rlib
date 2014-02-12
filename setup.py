from rlib import __author__, __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='rlib',
    version=__version__,
    packages=['rlib'],
    url='',
    license='',
    author=__author__,
    author_email='gardiner91@gmail.com',
    description=''
)
