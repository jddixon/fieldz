# fieldz/__init__.py

""" Welcome to the fieldz package. """

__version__ = '0.11.8'
__version_date__ = '2017-06-09'


__all__ = ['__version__', '__version_date__', 'FieldzError']


class FieldzError(RuntimeError):
    """ General error type. """
