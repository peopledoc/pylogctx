from __future__ import absolute_import

import logging

from celery.app import current_task
from celery.app.task import Task

from .core import context


logger = logging.getLogger(__name__)


class LoggingTask(Task):
    def __call__(self, *args, **kwargs):
        task = current_task()

        try:
            context.update(task)
        except Exception as e:
            logger.debug('Failed to push task to log context: %r', e)

        try:
            return super(LoggingTask, self).__call__(*args, **kwargs)
        finally:
            context.clear()
