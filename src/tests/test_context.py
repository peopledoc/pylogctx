import sys
import threading

from pylogctx.context import context as log_context
from tests.common_fixture import context


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
