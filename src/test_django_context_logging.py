import copy
from logging import LogRecord

import pytest
from django.core.exceptions import ImproperlyConfigured
from mock import patch, call

from django_context_logging import (
    ExtractRequestContextMiddleware, AddContextFormatter, AddContextFilter,
    _thread_local
)


@pytest.fixture()
def request():
    return {'rid'}


@pytest.fixture()
def record():
    return LogRecord("foo", "INFO", "foo", 10, "waagh :(", (), None)


@pytest.yield_fixture
def context():
    _thread_local.context = {'rid': 42}
    yield None
    del _thread_local.context


def _extractor(r):
    return r


def _failing_extractor(r):
    raise KeyError


def test_extract_request_context_middleware_no_extractor(request):
    with pytest.raises(ImproperlyConfigured):
        ExtractRequestContextMiddleware().process_request(request)


@patch('django_context_logging.settings',
            REQUEST_CONTEXT_EXTRACTOR=_failing_extractor)
def test_extract_request_context_middleware_extraction_failed(request):
    with patch('django_context_logging._log') as m:
        ExtractRequestContextMiddleware().process_request(request)
        assert m.method_calls == [call.exception()]


@patch('django_context_logging.settings', REQUEST_CONTEXT_EXTRACTOR=_extractor)
def test_extract_request_context_middleware_context_extracted(request):
    ExtractRequestContextMiddleware().process_request(request)
    assert _thread_local.context == request


def test_add_context_formatter_no_context(record):
    log = AddContextFormatter().format(record)
    assert log.strip() == record.message


def test_add_context_formatter_with_context(record, context):
    log = AddContextFormatter().format(record)
    assert log.strip() == '{} {}'.format(record.message, 'rid:42')


def test_add_context_filter_no_context_no_default(record):
    original_record = copy.deepcopy(record)
    AddContextFilter().filter(record)
    assert original_record.__dict__ == record.__dict__


def test_add_context_filter_no_context_with_default(record):
    original_record = copy.deepcopy(record)
    AddContextFilter(default={'rid': 4}).filter(record)
    assert record.__dict__.pop('rid') == 4
    assert original_record.__dict__ == record.__dict__


def test_add_context_filter_with_context(record, context):
    original_record = copy.deepcopy(record)
    AddContextFilter().filter(record)
    assert record.__dict__.pop('rid') == 42
    assert original_record.__dict__ == record.__dict__

