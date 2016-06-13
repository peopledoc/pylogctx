##################
 Using *pylogctx*
##################


.. contents:: Table of contents
   :backlinks: none


----


Setup logging
=============

You have two options to inject context to the log output: inject context as
extra fields in records or append context to the each message.


Using filter
------------

This method allow to pass fields to JSON formatters, SaaS log servers, etc. or
to use extra fields in format string.

.. code-block:: python

    LOGGING = {
        'version': 1,
        'formatters': {
            'extra': {
                # rid stands for request_id and comes from context
                'format': '%(levelname)s %(rid)s %(name)s %(message)s',
            },
        },
        'filters': {
            'context_filter': {
                # This filter inject context into each log records.
                '()': 'pylogctx.AddContextFilter',
                # Default values for string formatting
                'default': {'rid': None},
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'filters': ['context_filter'],
            },
        },
        # now setup your loggers...
    }


Using formatter
---------------

If you do not want to bother with custom log format and default context values
for a filter, you can use ``pylogctx.AddContextFormatter``.

.. code-block:: python

    LOGGING = {
        'version': 1,
        'formatters': {
            'append': {
                '()': 'pylogctx.AddContextFormatter'
                'format': '%(levelname)s %(name)s %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'append',
            },
        },
        # now setup your loggers...
    }

As you can see in this case we doesn't add any context related fields to a log
format string.  This is because ``pylogctx.AddContextFormatter``
will append all context information to every log message.


Feed the context
================

The context object is just a thread local instance. It is used as local
registry to inject shared fields in log records. Here is a full example:

.. code-block:: python

   from pylogctx.log import context as log_context


   log_context.update(userId=user.pk)
   # code, log, etc.
   for article in blog.articles:
       with log_context(articleId=article.pk):
           # code, log, ...
   # code, log, etc.
   log_context.remove('userId')
   ...
   log_context.clear()


Automatic feeding with middleware
---------------------------------

A middleware is provided to inject extra fields in context. It will also clear
the context after each requests.

.. code-block:: python

    MIDDLEWARE_CLASSES = [
        'pylogctx.django.ExtractRequestContextMiddleware',
        # rest middlewares...
    ]

    PYLOGCTX_REQUEST_EXTRACTOR = lambda request: {'rid': request.GET.getlist('rid')}


Here ``PYLOGCTX_REQUEST_EXTRACTOR`` is a callable which takes
``django.http.request.HttpRequest`` and returns dictionary with extracted
context.

**Note:** ``ExtractRequestContextMiddleware`` will fail with exception if no
``PYLOGCTX_REQUEST_EXTRACTOR`` specified.


Automatic feeding for celery task
---------------------------------

A task class is provided to inject clear log context after each task. Use it
like this.

.. code-block:: python

    app = Celery(task_cls='pylogctx.celery.LoggingTask')

    @app.task
    def my_task():
        logger.info("Logging from task!")


Adapt object to log record fields
---------------------------------

It can be cumbersome and error-prone to repeat every where in the codebase the
association *field name*, *object property*. *pylogctx* allow a simple way to
register adapter to class.

.. code-block::

    import uuid

    from pylogctx import log_adapter
    from django.http.request import HttpRequest

    @log_adapter(HttpRequest)
    def adapt_django_requests(request):
        return {
            djangoRequestId: str(uuid.uuid4()),
        }


Triggering the adapt logic is as easy as pushing the objects right into the
context.

.. code-block::

    from pylogctx import log_context

    log_context.update(request)


Dynamic context fields
----------------------

Sometime, you have a field that act as a watcher. e.g. a status of a business
object. This can pollute the code readability to update log_context after each
update of the object. This is why pylogctx ship a simple ``LazyAccessor`` util
you can put in the context.

.. code-block::

    from pylogctx import log_context, LazyAccessor

    log_context.update(status=LazyAccessor(self, status))

Beware that evaluating the accessor does not trigger a SQL query or any IO !


**That's all !!**

You're done! It's now up to you to provide meaning full log messages, fields
and to setup your app to send records to the log system.


.. image:: https://cdn.meme.am/instances/500x/66678465.jpg
   :align: center
   :alt: Logs everywhere!
