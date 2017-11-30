import pytest
from django.core.exceptions import ImproperlyConfigured
from mock import patch, call


from pylogctx.django import (
    ExtractRequestContextMiddleware,
    OuterMiddleware,
    context as log_context
)


from pylogctx import log_adapter


@pytest.fixture()
def request():
    return {'rid': 42}


@pytest.yield_fixture
def context():
    log_context.update(rid=42)
    yield log_context
    try:
        del log_context._stack
    except AttributeError:
        pass


def _extractor(r):
    return r


def _failing_extractor(r):
    raise KeyError


def test_middleware_no_extractor(request):
    with pytest.raises(ImproperlyConfigured):
        ExtractRequestContextMiddleware().process_request(request)


@patch('pylogctx.django.settings',
       PYLOGCTX_REQUEST_EXTRACTOR=_failing_extractor)
def test_middleware_extraction_failed(settings, request):
    with patch('pylogctx.django.logger') as m:
        ExtractRequestContextMiddleware().process_request(request)
        assert call.exception() in m.method_calls


@patch('pylogctx.django.settings', PYLOGCTX_REQUEST_EXTRACTOR=_extractor)
def test_middleware_context_extracted(settings, request, context):
    ExtractRequestContextMiddleware().process_request(request)
    fields = log_context.as_dict()
    assert 'rid' in fields


def test_middleware_context_cleaned_on_response(context):
    ExtractRequestContextMiddleware().process_response(None, None)
    assert not log_context.as_dict()


def test_middleware_context_cleaned_on_exception(context):
    ExtractRequestContextMiddleware().process_exception(None, None)
    assert not log_context.as_dict()


@patch.dict('pylogctx.core._adapter_mapping')
def test_middleware_adapter(request, context):
    @log_adapter(request.__class__)
    def adapter(request):
        return {
            'djangoRequestId': id(request),
        }

    OuterMiddleware().process_request(request)
    fields = log_context.as_dict()
    assert 'djangoRequestId' in fields


def test_middleware_missing_adapter(request, context):
    OuterMiddleware().process_request(request)
