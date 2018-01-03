from __future__ import absolute_import

import logging

from celery import current_task
from celery import Task

from .core import context


logger = logging.getLogger(__name__)


class LoggingTask(Task):

    def before_call(self):
        # Override if you need to add some vars or log something.
        pass

    def after_call(self):
        # Override if you need to add some vars or log something.
        pass

    def __call__(self, *args, **kwargs):
        # Save context to put in back at the end. Useful when a task call
        # another task to avoid context from another task.
        self.save_context = context.as_dict()
        context.clear()

        self.before_call()
        task = current_task

        try:
            context.update(task)
        except Exception as e:
            logger.debug('Failed to push task to log context: %r', e)

        try:
            return super(LoggingTask, self).__call__(*args, **kwargs)
        finally:
            self.after_call()
            context.clear()
            if self.save_context:
                context.update(**self.save_context)
