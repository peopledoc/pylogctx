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
    ({'name': 'toto'}, {'name': 'tata'}, {'name': 'tata'}),
    ({'name': 'toto', 'hobbies': ['programming', 'chess']},
     {'hobbies': ['gaming']},
     {'name': 'toto', 'hobbies': ['programming', 'chess', 'gaming']}),
    ({'name': 'toto', 'hobbies': None},
     {'hobbies': ['gaming']},
     {'name': 'toto', 'hobbies': ['gaming']}),
    ({'name': 'toto', 'hobbies': {'programming', 'chess'}},
     {'hobbies': {'gaming'}},
     {'name': 'toto', 'hobbies': {'programming', 'chess', 'gaming'}}),
    ({'name': 'toto', 'hobbies': None},
     {'hobbies': {'gaming'}},
     {'name': 'toto', 'hobbies': {'gaming'}}),
    ({'name': 'toto', 'hobbies': {'gaming': None}},
     {'hobbies': {'gaming': {'play': 'foo'}}},
     {'name': 'toto', 'hobbies': {'gaming': {'play': 'foo'}}}),
    ({'name': {"toto": 1}, 'hobbies': ['programming', 'chess']},
     {'name': {"tata": 2}},
     {'name': {"toto": 1, "tata": 2},
      'hobbies': ['programming', 'chess']}),
])
def test_deepupdate(target, src, result):
    deepupdate(target, src)
    assert target == result
