from celery import Celery
from celery.app import current_task
from celery.utils.log import get_task_logger
from celery import VERSION

from mock import patch


def test_task():
    from pylogctx import context

    app = Celery(task_cls='pylogctx.celery.LoggingTask')

    @app.task
    def my_task():
        context.update(taskField='RUNNED')
        logger = get_task_logger(current_task().name)
        logger.info("I log!")
        return context.as_dict()

    result = my_task.apply()
    if VERSION.major < 4:
        result.maybe_reraise()
    else:
        result.maybe_throw()
    fields = result.result
    assert 'taskField' in fields
    assert not context.as_dict()


def test_failing():
    from pylogctx import context

    app = Celery(task_cls='pylogctx.celery.LoggingTask')

    @app.task
    def my_task():
        raise Exception('fail!')

    result = my_task.apply()
    assert isinstance(result.result, Exception)
    assert not context.as_dict()


@patch.dict('pylogctx.core._adapter_mapping')
def test_adapter():
    from pylogctx import context, log_adapter

    app = Celery(task_cls='pylogctx.celery.LoggingTask')

    @app.task
    def my_task():
        return context.as_dict()

    @log_adapter(app.Task)
    def adapter(task):
        return {
            'celeryTaskId': task.request.id,
            'celeryTask': task.name
        }

    result = my_task.apply()
    if VERSION.major < 4:
        result.maybe_reraise()
    else:
        result.maybe_throw()

    fields = result.result
    assert 'celeryTask' in fields
    assert 'celeryTaskId' in fields
