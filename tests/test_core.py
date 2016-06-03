import copy
from logging import LogRecord
import sys
import threading

import pytest

from pylogctx import (
    AddContextFormatter, AddContextFilter, context as log_context
)


@pytest.fixture()
def record():
    return LogRecord("foo", "INFO", "foo", 10, "waagh :(", (), None)


@pytest.yield_fixture
def context():
    log_context.update(rid=42)
    yield None
    try:
        del log_context._stack
    except AttributeError:
        pass


def test_formatter_no_context(record):
    log = AddContextFormatter().format(record)
    assert log.strip() == record.message


def test_formatter_with_context(record, context):
    log = AddContextFormatter().format(record)
    assert log.strip() == '{} {}'.format(record.message, 'rid:42')


def test_filter_no_context_no_default(record):
    original_record = copy.deepcopy(record)
    AddContextFilter().filter(record)
    assert original_record.__dict__ == record.__dict__


def test_filter_no_context_with_default(record, context):
    AddContextFilter(default={'default': 4}).filter(record)
    assert record.default == 4
    assert record.rid == 42


def test_filter_with_context(record, context):
    original_record = copy.deepcopy(record)
    AddContextFilter().filter(record)
    assert record.__dict__.pop('rid') == 42
    assert original_record.__dict__ == record.__dict__


def test_update_clear_remove(context):
    log_context.update(myField='toto', myOtherField='titi')
    fields = log_context.as_dict()
    assert 'myField' in fields
    assert 'myOtherField' in fields

    log_context.remove('myOtherField')
    fields = log_context.as_dict()
    assert 'myField' in fields
    assert 'myOtherField' not in fields

    log_context.clear()
    fields = log_context.as_dict()
    assert 'myField' not in fields


def test_context_manager(context):
    # Check two level stack in log context
    with log_context(myField='toto'):
        fields = log_context.as_dict()
        assert 'myField' in fields

        with log_context(myOtherField='toto'):
            fields = log_context.as_dict()
            assert 'myOtherField' in fields
            assert 'myField' in fields

        fields = log_context.as_dict()
        assert 'myField' in fields
        assert ('myOtherField', fields)

    fields = log_context.as_dict()
    assert ('myField', fields)


def test_multi_thread(context):
    # Create a simple child thread updating in log context, but NOT clearing
    # context.
    class Child(threading.Thread):
        def __init__(self, shm):
            super(Child, self).__init__()
            self.shm = shm

        def run(self):
            try:
                log_context.update(childField='titi')
                fields = log_context.as_dict()
                assert 'childField' in fields
            except (AssertionError, Exception):
                self.case.shm['thread_exc_info'] = sys.exc_info()

    # Run it
    shm = dict(thread_exc_info=None)
    child = Child(shm)
    child.start()
    child.join()

    # Ensure child success
    assert shm['thread_exc_info'] is None

    # Check caller context is safe :-)
    fields = log_context.as_dict()
    assert 'childField'not in fields
