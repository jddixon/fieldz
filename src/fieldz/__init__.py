# fieldz/__init__.py

""" Welcome to the fieldz package. """

__version__ = '0.11.13'
__version_date__ = '2017-12-30'


__all__ = ['__version__', '__version_date__', 'FieldzError']


class FieldzError(RuntimeError):
    """ General error type. """
