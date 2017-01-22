# fieldz/__init__.py

""" Welcome to the fieldz package. """

__version__ = '0.11.2'
__version_date__ = '2017-01-21'


__all__ = ['__version__', '__version_date__', 'FieldzError']


class FieldzError(RuntimeError):
    """ General error type. """
