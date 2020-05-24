# coding: utf-8
from __future__ import unicode_literals

import copy
from logging import LogRecord
import sys
import threading

from mock import patch
import pytest
import six

from pylogctx import (
    AddContextFormatter, AddContextFilter, ExcInfoFilter,
    context as log_context,
)


@pytest.fixture()
def record():
    return LogRecord("foo", "INFO", "foo", 10, "waagh :(", (), None)


@pytest.yield_fixture
def context():
    log_context.update(rid=42)
    yield log_context
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
        assert 'myOtherField' not in fields

    fields = log_context.as_dict()
    assert 'myField' not in fields


def test_deep_update_dict(context):
    log_context.remove('rid')

    # Value to dict update override
    log_context.update(myField={'toto': {'tata1': {'titi1': 'tutu'}}})
    fields = log_context.as_dict()
    assert fields == {'myField': {'toto': {'tata1': {'titi1': 'tutu'}}}}

    # Update tata1 to add titi2
    log_context.update(myField={'toto': {'tata1': {'titi2': 'tutu'}}})
    fields = log_context.as_dict()
    assert fields == {
        'myField': {'toto': {'tata1': {'titi1': 'tutu', 'titi2': 'tutu'}}}}

    # Override value `tata1/titi1`
    log_context.update(myField={'toto': {'tata1': {'titi1': 'val'}}})
    fields = log_context.as_dict()

    assert fields == {
        'myField': {'toto': {'tata1': {'titi1': 'val',
                                       'titi2': 'tutu'}}}}


def test_deep_update_dict_context_manger(context):
    log_context.remove('rid')
    with log_context(myField={'toto': {'tata1': {'titi1': 'tutu'}}}):
        fields = log_context.as_dict()
        assert fields == {'myField': {'toto': {'tata1': {'titi1': 'tutu'}}}}

        # Update tata1 to add titi2
        with log_context(myField={'toto': {'tata1': {'titi2': 'tutu'}}}):
            fields = log_context.as_dict()
            assert fields == {
                'myField': {
                    'toto': {'tata1': {'titi1': 'tutu', 'titi2': 'tutu'}}}}

            # Override value `tata1/titi1`
            with log_context(myField={'toto': {'tata1': {'titi1': 'val'}}}):
                fields = log_context.as_dict()
                assert fields == {
                    'myField': {'toto': {'tata1': {'titi1': 'val',
                                                   'titi2': 'tutu'}}}}

    fields = log_context.as_dict()
    assert 'myField' not in fields


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


@patch.dict('pylogctx.core._adapter_mapping')
def test_adapter_mro(context):
    from pylogctx import log_adapter

    class Parent(object):
        pass

    class Child1(Parent):
        name = "child1"

    class Child2(Parent):
        name = "child2"

    @log_adapter(Parent)
    def parent_log_maker(instance):
        return {instance.name: id(instance)}

    child1 = Child1()
    child2 = Child2()
    context.update(child1, child2)

    data = context.as_dict()
    assert child1.name in data
    assert child2.name in data


@patch.dict('pylogctx.core._adapter_mapping')
def test_adapter_manager(context):
    from pylogctx import log_adapter

    class Parent(object):
        pass

    class Child1(Parent):
        name = "child1"

    class Child2(Parent):
        name = "child2"

    @log_adapter(Parent)
    def parent_log_maker(instance):
        return {instance.name: id(instance)}

    child1 = Child1()
    child2 = Child2()
    with context(child1, child2):
        data = context.as_dict()
        assert child1.name in data
        assert child2.name in data


@patch.dict('pylogctx.core._adapter_mapping')
def test_adapter_with_parameters(context):
    from pylogctx import log_adapter

    class Parent(object):
        pass

    class Child(Parent):
        pass

    @log_adapter(Parent)
    def parent_log_maker(instance, with_child=False):
        fields = dict(parent=id(instance))
        if with_child:
            fields.update({"child": {'baby2': 'tutu'}})
        return fields

    log_context.update(child={'baby1': 'toto'})

    with context.cm_update_one(Child(), with_child=True):
        data = context.as_dict()
        assert 'parent' in data
        assert 'child' in data
        assert 'baby1' in data['child']
        assert 'baby2' in data['child']

    context.update_one(Child(), with_child=True)
    data = context.as_dict()
    assert 'parent' in data
    assert 'child' in data
    assert 'baby1' in data['child']
    assert 'baby2' in data['child']


@patch.dict('pylogctx.core._adapter_mapping')
def test_adapter_missing(context):
    with pytest.raises(Exception):
        context.update(object())


def test_lazy_accessor():
    from pylogctx import LazyAccessor

    class MyAttribute(object):
        str_repr = 'MyObject'

        def __repr__(self):
            return '<MyObject>'

        def __str__(self):
            return self.str_repr

        def __unicode__(self):
            return 'обѥѩкт'

    class MyObject(object):
        attribute = MyAttribute()

    instance = MyObject()
    value = LazyAccessor(instance, 'attribute')

    assert 'MyObject' == str(value)
    assert '<MyObject>' == repr(value)
    if six.PY2:
        assert 'обѥѩкт' == unicode(value)
    else:
        MyObject.attribute.str_repr = 'обѥѩкт'
        assert 'обѥѩкт' == str(value)


def test_lazy_accessor_deepupdate(context):
    log_context.remove('rid')

    from pylogctx import LazyAccessor

    class MyObject(object):
        value = 'foo'

        def __repr__(self):
            return 'foo'

    instance = MyObject()
    lazy_instance = LazyAccessor(instance, 'value')

    log_context.update(lazy_instance=lazy_instance)

    fields = log_context.as_dict()
    assert str(fields['lazy_instance']) == 'foo'

    # Check value change for LazyAccessor
    instance.value = 'bar'

    fields = log_context.as_dict()
    assert str(fields['lazy_instance']) == 'bar'


def test_lazy_accessor_deepupdate_nested(context):
    log_context.remove('rid')

    from pylogctx import LazyAccessor

    class MyObject(object):
        value = 'foo'

        def __repr__(self):
            return 'foo'

    instance = MyObject()
    lazy_instance = LazyAccessor(instance, 'value')

    log_context.update(parent={"lazy_instance": lazy_instance,
                               "foo": "bar"})

    fields = log_context.as_dict()
    assert str(fields['parent']['lazy_instance']) == 'foo'

    # Check value change for LazyAccessor
    instance.value = 'bar'

    fields = log_context.as_dict()
    assert str(fields['parent']['lazy_instance']) == 'bar'


def test_filter_exc_info(record):
    record.exc_info = object()
    ExcInfoFilter().filter(record)
    assert not record.exc_info

def test_update_with_prefix_happy_path(context):
    @log_context.prefix("test")
    def _dummy():
        log_context.update(foo="bar", baz="qux", fourtytwo=42)

    _dummy()
    log_context.update(noprefix="please")

    assert log_context.as_dict() == {
        "rid": 42,
        "test__foo": "bar",
        "test__baz": "qux",
        "test__fourtytwo": 42,
        "noprefix": "please"
    }

    log_context.clear()

    @log_context.prefix("deadbeef", separator=":")
    def _dummy():
        log_context.update(foo="bar", baz="qux", fourtytwo=42)

    _dummy()

    assert log_context.as_dict() == {
        "deadbeef:foo": "bar",
        "deadbeef:baz": "qux",
        "deadbeef:fourtytwo": 42,
    }


def test_update_with_prefix_exception_raised(context):
    @log_context.prefix("test")
    def _dummy():
        log_context.update(foo="bar")
        raise Exception("I'm a teapot")

    with pytest.raises(Exception):
        _dummy()

    # We continue on, context shouldn't be cleared
    log_context.update(noprefix="please")
    assert log_context.as_dict() == {
        "rid": 42,
        "test__foo": "bar",
        "noprefix": "please",
    }

def test_update_with_nested_prefix(context):
    @log_context.prefix("foo")
    def _dummy():
        log_context.update(level=1)

        @log_context.prefix("bar", separator=":")
        def _dummy2():
            log_context.update(level=2)
            return None
        return _dummy2()

    _dummy()
    log_context.update(noprefix="please")

    assert log_context.as_dict() == {
        "rid": 42,
        "foo__level": 1,
        "foo__bar:level": 2,
        "noprefix": "please"
    }

def test_values_passed_to_with_prefix(context):
    class NoString(object):
        def __str__(self):
            raise Exception("Don't make me a string!")

    with pytest.raises(ValueError):
        @log_context.prefix(prefix=NoString())
        def _dummy():
            log_context.update(failed=True)
        _dummy()

    with pytest.raises(ValueError):
        @log_context.prefix(prefix="goodboi", separator=NoString())
        def _dummy():
            log_context.update(failed=True)
        _dummy()
