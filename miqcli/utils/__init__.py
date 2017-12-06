from types import FunctionType

__all__ = ['get_class_methods']


def get_class_methods(cls):
    """Return a list of class methods.

    Does a lookup on the given class supplied to round up all methods.

    :param cls: Class to lookup.
    :type cls: class
    :return: List of class methods.
    :rtype: list
    """
    methods = list()
    for key, value in cls.__dict__.items():
        if not isinstance(value, FunctionType):
            continue
        methods.append(key)
    methods.sort()
    return methods
