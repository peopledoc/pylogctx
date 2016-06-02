import copy
from logging import LogRecord

from django.core.exceptions import ImproperlyConfigured
from mock import patch, call
import pytest

from pylogctx.context import context as log_context
from pylogctx.ext.django import (
    ExtractRequestContextMiddleware, AddContextFormatter, AddContextFilter
)
from tests.common_fixture import context


@pytest.fixture()
def request():
    return {'rid': 42}


@pytest.fixture()
def record():
    return LogRecord("foo", "INFO", "foo", 10, "waagh :(", (), None)


def _extractor(r):
    return r


def _failing_extractor(r):
    raise KeyError


def test_extract_request_context_middleware_no_extractor(request):
    with pytest.raises(ImproperlyConfigured):
        ExtractRequestContextMiddleware().process_request(request)


@patch('pylogctx.ext.django.settings',
       DJANGO_CONTEXT_LOGGING_EXTRACTOR=_failing_extractor)
def test_extract_request_context_middleware_extraction_failed(request):
    with patch('pylogctx.ext.django._log') as m:
        ExtractRequestContextMiddleware().process_request(request)
        assert m.method_calls == [call.exception()]


@patch('pylogctx.ext.django.settings',
       DJANGO_CONTEXT_LOGGING_EXTRACTOR=_extractor)
def test_extract_request_context_middleware_context_extracted(request, context):  # noqa
    ExtractRequestContextMiddleware().process_request(request)
    fields = log_context.as_dict()
    assert 'rid' in fields


def test_extract_request_context_middleware_context_cleaned_on_response(context):  # noqa
    ExtractRequestContextMiddleware().process_response(None, None)
    assert not log_context.as_dict()


def test_extract_request_context_middleware_context_cleaned_on_exception(context):  # noqa
    ExtractRequestContextMiddleware().process_exception(None, None)
    assert not log_context.as_dict()


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


