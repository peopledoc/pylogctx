from celery import Celery, current_task
from celery.utils.log import get_task_logger
from celery import VERSION

import pytest

from pylogctx.celery import LoggingTask


def test_task():
    from pylogctx import context

    app = Celery(task_cls=LoggingTask)

    @app.task
    def my_task():
        context.update(taskField="RUNNED")
        logger = get_task_logger(current_task.name)
        logger.info("I log!")
        return context.as_dict()

    result = my_task.apply()
    if VERSION.major < 4:
        result.maybe_reraise()
    else:
        result.maybe_throw()
    fields = result.result
    assert "taskField" in fields
    assert not context.as_dict()


class OldLoggingTask(LoggingTask):
    def before_call(self):
        from pylogctx import context

        context.update(taskField="RUNNED")


def test_old_task():
    from pylogctx import context

    app = Celery(task_cls=OldLoggingTask)

    @app.task
    def my_task():
        logger = get_task_logger(current_task.name)
        logger.info("I log!")
        return context.as_dict()

    with pytest.warns(
        UserWarning, match="Method `before_call` without args is deprecated"
    ):
        result = my_task.apply()

    if VERSION.major < 4:
        result.maybe_reraise()
    else:
        result.maybe_throw()
    fields = result.result
    assert "taskField" in fields
    assert not context.as_dict()


def test_failing():
    from pylogctx import context

    app = Celery(task_cls=LoggingTask)

    @app.task
    def my_task():
        raise Exception("fail!")

    result = my_task.apply()
    assert isinstance(result.result, Exception)
    assert not context.as_dict()


def test_adapter(mocker):
    mocker.patch.dict("pylogctx.core._adapter_mapping")
    from pylogctx import context, log_adapter

    # To fill save context
    context.update(toto="tata")
    fields = context.as_dict()
    assert "toto" in fields

    app = Celery(task_cls="pylogctx.celery.LoggingTask")

    @log_adapter(app.Task)
    def adapter(task):
        return {"celeryTaskId": task.request.id, "celeryTask": task.name}

    @app.task
    def my_task():
        return context.as_dict()

    result = my_task.apply()
    if VERSION.major < 4:
        result.maybe_reraise()
    else:
        result.maybe_throw()

    fields = result.result
    assert "celeryTask" in fields
    assert "celeryTaskId" in fields

    # Check context is the same before task was started
    fields = context.as_dict()
    assert "toto" in fields

    context.clear()  # Clear context
