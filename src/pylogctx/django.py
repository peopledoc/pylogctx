from __future__ import absolute_import

import logging

from django.conf import settings

from pylogctx import context, AdapterNotFound


logger = logging.getLogger(__name__)


class OuterMiddleware(object):
    def process_request(self, request):
        context.clear()
        try:
            context.update(request)
        except AdapterNotFound:
            logger.info("Can't adapt %s for log.", request.__class__.__name__)

    def process_response(self, request, response):
        context.clear()
        return response

    def process_exception(self, request, exception):
        context.clear()
        return None


class ExtractRequestContextMiddleware(OuterMiddleware):
    def process_request(self, request):
        context.clear()
        extractor = settings.PYLOGCTX_REQUEST_EXTRACTOR
        try:
            context.update(**extractor(request))
        except Exception:
            logger.exception()
