from __future__ import absolute_import

import logging

from django.conf import settings

from pylogctx import context


logger = logging.getLogger(__name__)


class ExtractRequestContextMiddleware(object):
    def process_request(self, request):
        extractor = settings.PYLOGCTX_REQUEST_EXTRACTOR
        try:
            context.update(**extractor(request))
        except Exception:
            logger.exception()

    def process_response(self, request, response):
        context.clear()
        return response

    def process_exception(self, request, exception):
        context.clear()
        return None
