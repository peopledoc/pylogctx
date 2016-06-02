import logging

from django.conf import settings

from pylogctx.context import context

_log = logging.getLogger(__name__)


class ExtractRequestContextMiddleware(object):
    def process_request(self, request):
        extractor = settings.DJANGO_CONTEXT_LOGGING_EXTRACTOR
        try:
            context.update(**extractor(request))
        except Exception:
            _log.exception()

    def process_response(self, request, response):
        context.clear()
        return response

    def process_exception(self, request, exception):
        context.clear()
        return None


class AddContextFilter(logging.Filter):
    def __init__(self, name='', default=None):
        super(AddContextFilter, self).__init__(name)
        self.default = default or {}

    def filter(self, record):
        record.__dict__.update(context.as_dict() or self.default)
        return True


class AddContextFormatter(logging.Formatter):
    def format(self, record):
        msg = super(AddContextFormatter, self).format(record)
        context_str = u' '.join([
            u'{}:{}'.format(k, v) for k, v in context.items()
        ])
        return u'{msg} {context}'.format(msg=msg, context=context_str)
