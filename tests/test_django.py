import pytest
from django.core.exceptions import ImproperlyConfigured
from mock import patch, call


from pylogctx.django import (
    ExtractRequestContextMiddleware,
    OuterMiddleware,
    context as log_context
)


from pylogctx import log_adapter


@pytest.fixture
def django_test_settings(monkeypatch):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "settings")

@pytest.fixture()
def mock_request():
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


def test_middleware_no_extractor(mock_request):
    with pytest.raises(ImproperlyConfigured):
        ExtractRequestContextMiddleware().process_request(mock_request)


@patch('pylogctx.django.settings',
       PYLOGCTX_REQUEST_EXTRACTOR=_failing_extractor)
def test_middleware_extraction_failed(settings, mock_request, django_test_settings):
    with patch('pylogctx.django.logger') as m:
        ExtractRequestContextMiddleware().process_request(mock_request)
        assert call.exception() in m.method_calls


@patch('pylogctx.django.settings', PYLOGCTX_REQUEST_EXTRACTOR=_extractor)
def test_middleware_context_extracted(settings, mock_request, context, django_test_settings):
    ExtractRequestContextMiddleware().process_request(mock_request)
    fields = log_context.as_dict()
    assert 'rid' in fields


def test_middleware_context_cleaned_on_response(context):
    ExtractRequestContextMiddleware().process_response(None, None)
    assert not log_context.as_dict()


def test_middleware_context_cleaned_on_exception(context):
    ExtractRequestContextMiddleware().process_exception(None, None)
    assert not log_context.as_dict()


@patch.dict('pylogctx.core._adapter_mapping')
def test_middleware_adapter(mock_request, context):
    @log_adapter(mock_request.__class__)
    def adapter(mock_request):
        return {
            'djangoRequestId': id(mock_request),
        }

    OuterMiddleware().process_request(mock_request)
    fields = log_context.as_dict()
    assert 'djangoRequestId' in fields


def test_middleware_missing_adapter(mock_request, context):
    OuterMiddleware().process_request(mock_request)
