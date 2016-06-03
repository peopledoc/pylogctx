from celery import Celery
from celery.app import current_task
from celery.utils.log import get_task_logger


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
    result.maybe_reraise()
    fields = result.result
    assert 'taskField' in fields
    assert 'celeryTask' in fields
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
