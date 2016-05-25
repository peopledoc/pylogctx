import logging
import threading

from django.conf import settings


_thread_local = threading.local()
_log = logging.getLogger(__name__)


class ExtractRequestContextMiddleware(object):
    def process_request(self, request):
        extractor = settings.DJANGO_CONTEXT_LOGGING_EXTRACTOR
        try:
            _thread_local.context = extractor(request)
        except Exception:
            _log.exception()


class AddContextFilter(logging.Filter):
    def __init__(self, name='', default=None):
        super(AddContextFilter, self).__init__(name)
        self.default = default or {}

    def filter(self, record):
        context = getattr(_thread_local, 'context', self.default)
        for k, v in context.items():
            setattr(record, k, v)
        return True


class AddContextFormatter(logging.Formatter):
    def format(self, record):
        context = getattr(_thread_local, 'context', {})
        msg = super(AddContextFormatter, self).format(record)
        context_str = u' '.join([
            u'{}:{}'.format(k, v) for k, v in context.items()
        ])
        return u'{msg} {context}'.format(msg=msg, context=context_str)
