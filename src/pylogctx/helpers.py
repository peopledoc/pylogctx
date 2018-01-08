from __future__ import absolute_import

import copy
import logging

from django.db import models

logger = logging.getLogger(__name__)


def prevent_django_model(value):

    # Detect value is an instance from django model to warn before a deepcopy.
    # Indeed when an django model object is "deepcopied",
    # all these relationships are fetched.
    if isinstance(value, models.Model):
        logger.warning("[Pylogctx] Be careful an django model object: %s is "
                       "deepcopying", value)


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
                prevent_django_model(v)
                target[k] = copy.deepcopy(v)
