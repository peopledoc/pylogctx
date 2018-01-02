# coding: utf-8
from __future__ import unicode_literals

import pytest
from pylogctx.helpers import deepupdate


@pytest.mark.parametrize("target, src, result", [
    ({}, {}, {}),
    ({}, None, {}),
    ({}, 2, {}),
    ({}, [2], {}),
    ({}, {2}, {}),
    ({'name': 'toto'}, {}, {'name': 'toto'}),
    ({}, {'name': 'toto'}, {'name': 'toto'}),
    ({'name': 'toto'}, {'name': 'toto'}, {'name': 'toto'}),
    ({'name': 'toto', 'hobbies': ['programming', 'chess']},
     {'hobbies': ['gaming']},
     {'name': 'toto', 'hobbies': ['programming', 'chess', 'gaming']}),
    ({'name': 'toto', 'hobbies': {'programming', 'chess'}},
     {'hobbies': {'gaming'}},
     {'name': 'toto', 'hobbies': {'programming', 'chess', 'gaming'}}),
    ({'name': {"toto": 1}, 'hobbies': ['programming', 'chess']},
     {'name': {"toto2": 2}},
     {'name': {"toto": 1, "toto2": 2},
      'hobbies': ['programming', 'chess']}),
])
def test_deepupdate(target, src, result):
    deepupdate(target, src)
    print (target)
    assert target == result
