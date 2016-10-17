#!/usr/bin/python3

# ~/dev/py/fieldz/setup.py

""" Set up fieldz package. """

import re
from distutils.core import setup
__version__ = re.search(r"__version__\s*=\s*'(.*)'",
                        open('fieldz/__init__.py').read()).group(1)

# see http://docs.python.org/distutils/setupscript.html

setup(name='fieldz',
      version=__version__,
      author='Jim Dixon',
      author_email='jddixon@gmail.com',
      #
      # wherever we have a .py file that will be imported, we
      # list it here, without the extension but SQuoted
      py_modules=[],
      #
      # a package has its own directory with an __init__.py in it
      packages=['fieldz',
                'fieldz/compiler',      # a mistake ? XXX
                'fieldz/reg',
                ],
      #
      # scripts should have a globally unique name; they might be in a
      #   scripts/ subdir; SQuote the script name
      scripts=['fieldzSpecc'],
      description='python3 protocol for compressing/decompressing data',
      url='https://jddixon.github.io/fieldz',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python 3',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      )
