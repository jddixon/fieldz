#!/usr/bin/python3

# ~/dev/py/fieldz/setup.py

import re
from distutils.core import setup
__version__ = re.search("__version__\s*=\s*'(.*)'",
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
      # MISSING description
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
      ],
      )
