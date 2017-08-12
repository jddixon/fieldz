#!/usr/bin/python3
# fieldz/setup.py

""" Setuptools project configuration for fieldz. """

from os.path import exists
from setuptools import setup

long_desc = None
if exists('README.md'):
    with open('README.md', 'r') as file:
        long_desc = file.read()

setup(name='fieldz',
      version='0.11.10',
      author='Jim Dixon',
      author_email='jddixon@gmail.com',
      long_description=long_desc,
      packages=['fieldz', 'fieldz.compiler'],
      package_dir={'': 'src'},
      py_modules=[],
      include_package_data=False,
      zip_safe=False,
      scripts=['src/fieldzSpecc'],
      description='python3 protocol for compressing/decompressing data',
      url='https://jddixon.github.io/fieldz',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python 2.7',
          'Programming Language :: Python 3.3',
          'Programming Language :: Python 3.4',
          'Programming Language :: Python 3.5',
          'Programming Language :: Python 3.6',
          'Programming Language :: Python 3.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],)
