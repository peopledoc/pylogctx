import pytest

from pylogctx.context import context as log_context


@pytest.yield_fixture
def context():
    log_context.update(rid=42)
    yield None
    try:
        del log_context._stack
    except AttributeError:
        pass
