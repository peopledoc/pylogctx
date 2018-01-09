import copy


def deepcopy_wrapper(value):
    """Wrapper to check value before deepcopy
    Indeed when an ORM object is "deepcopied",
    all these relationships are fetched.

    Override example:
    >>> from django.db import models
    >>> def deepcopy_wrapper(value):
    >>>     if isinstance(value, models.Model):
    >>>         logger.warning('[Pylogctx] Be careful an django model '
    >>>                        'object: %s is "deepcopying"', value)
    >>>     return copy.deepcopy(value)
    """
    return copy.deepcopy(value)


def deepupdate(target, src):
    """Deep update target dict with src
    For each k,v in src: if k doesn't exist in target, it is deep copied from
    src to target. Otherwise, if v is a list, target[k] is extended with
    src[k]. If v is a set, target[k] is updated with v, If v is a dict,
    recursively deep-update it.

    Examples:
    >>> t = {'name': 'toto', 'hobbies': ['programming', 'chess']}
    >>> deepupdate(t, {'hobbies': ['gaming']})
    >>> print t
    {'name': 'toto', 'hobbies': ['programming', 'chess', 'gaming']}
    """
    if src and isinstance(src, dict):
        for k, v in src.items():
            if k in target and isinstance(v, (list, dict, set)):
                if isinstance(v, list):
                    target[k].extend(v)
                elif isinstance(v, dict):
                    deepupdate(target[k], v)
                elif isinstance(v, set):
                    target[k].update(v)
            else:
                target[k] = deepcopy_wrapper(v)
