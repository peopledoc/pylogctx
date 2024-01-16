from django.http import HttpResponse
import pytest


from pylogctx.django import (
    ExtractRequestContextMiddleware,
    OuterMiddleware,
    context as log_context
)


from pylogctx import log_adapter


@pytest.fixture()
def http_request():
    return {'rid': 42}


@pytest.fixture()
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


def test_middleware_no_extractor(http_request):
    with pytest.raises(AttributeError):
        ExtractRequestContextMiddleware(HttpResponse).process_request(http_request)


def test_middleware_extraction_failed(settings, mocker, http_request):
    settings.PYLOGCTX_REQUEST_EXTRACTOR = _failing_extractor
    logger_mock = mocker.patch('pylogctx.django.logger')

    ExtractRequestContextMiddleware(HttpResponse).process_request(http_request)
    assert mocker.call.exception("Can't use extractor") in logger_mock.method_calls


def test_middleware_context_extracted(settings, http_request, context):
    settings.PYLOGCTX_REQUEST_EXTRACTOR = _extractor

    ExtractRequestContextMiddleware(HttpResponse).process_request(http_request)
    fields = log_context.as_dict()
    assert 'rid' in fields


def test_middleware_context_cleaned_on_response(context):
    ExtractRequestContextMiddleware(HttpResponse).process_response(None, None)
    assert not log_context.as_dict()


def test_middleware_context_cleaned_on_exception(context):
    ExtractRequestContextMiddleware(HttpResponse).process_exception(None, None)
    assert not log_context.as_dict()


def test_middleware_adapter(mocker, http_request, context):
    mocker.patch.dict('pylogctx.core._adapter_mapping')

    @log_adapter(http_request.__class__)
    def adapter(http_request):
        return {
            'djangoRequestId': id(http_request),
        }

    OuterMiddleware(HttpResponse).process_request(http_request)
    fields = log_context.as_dict()
    assert 'djangoRequestId' in fields


def test_middleware_missing_adapter(http_request, context):
    OuterMiddleware(HttpResponse).process_request(http_request)
