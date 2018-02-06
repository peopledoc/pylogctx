from __future__ import absolute_import

import logging
import inspect
import warnings

from celery import current_task
from celery import Task

from .core import context


logger = logging.getLogger(__name__)


class LoggingTask(Task):

    def before_call(self, *args, **kwargs):
        # Override if you need to add some vars or log something.
        pass

    def after_call(self, *args, **kwargs):
        # Override if you need to add some vars or log something.
        pass

    def __call__(self, *args, **kwargs):
        # Save context to put in back at the end. Useful when a task call
        # another task to avoid context from another task.
        self.save_context = context.as_dict()
        context.clear()

        args_repr = inspect.getargspec(self.before_call)
        if args_repr.varargs is None:
            # To keep breaking compat
            warnings.warn('Method `before_call` without args is deprecated')
            self.before_call()
        else:
            self.before_call(*args, **kwargs)

        task = current_task

        try:
            context.update(task)
        except Exception as e:
            logger.debug('Failed to push task to log context: %r', e)

        try:
            return super(LoggingTask, self).__call__(*args, **kwargs)
        finally:
            args_repr = inspect.getargspec(self.after_call)
            if args_repr.varargs is None:
                # To keep breaking compat
                warnings.warn('Method `after_call` without args is deprecated')
                self.after_call()
            else:
                self.after_call(*args, **kwargs)
            context.clear()
            if self.save_context:
                context.update(**self.save_context)
