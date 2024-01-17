import logging
import warnings
from inspect import getfullargspec

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

        arg_spec = getfullargspec(self.before_call)
        if arg_spec.varargs is None:
            # To keep breaking compat
            warnings.warn(
                'Method `before_call` without args is deprecated', stacklevel=1
            )
            self.before_call()
        else:
            self.before_call(*args, **kwargs)

        task = current_task

        try:
            context.update(task)
        except Exception as e:
            logger.debug('Failed to push task to log context: %r', e)

        try:
            return super().__call__(*args, **kwargs)
        finally:
            arg_spec = getfullargspec(self.after_call)
            if arg_spec.varargs is None:
                # To keep breaking compat
                warnings.warn(
                    'Method `after_call` without args is deprecated',
                    stacklevel=1,
                )
                self.after_call()
            else:
                self.after_call(*args, **kwargs)
            context.clear()
            if self.save_context:
                context.update(**self.save_context)
