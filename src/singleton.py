"""@package docstring

Module for defining a metaclass that allows for the creation of Singletons.
"""

class Singleton(type):
    """Python metasclass for creating singletons in other classes"""
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
