import inspect


def getargspec(callable):
    try:
        # Python 3
        return inspect.getfullargspec(callable)
    except AttributeError:
        # Python 2
        return inspect.getargspec(callable)
