from __future__ import absolute_import

from celery.app import current_task
from celery.app.task import Task

from .core import context


class LoggingTask(Task):
    def __call__(self, *args, **kwargs):
        task = current_task()
        context.update(
            celeryTask=task.name,
            celeryTaskId=task.request.id,
        )
        try:
            return super(LoggingTask, self).__call__(*args, **kwargs)
        finally:
            context.clear()
