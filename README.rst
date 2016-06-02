.. image:: https://travis-ci.org/lorehov/django_context_logging.svg
    :target: https://travis-ci.org/lorehov/django_context_logging
    :alt: Build Status

########################
 Django Context Logging
########################

``django_context_logging`` is a library for enriching logs records with context
fields.  Typical usage is for adding some request_id to all logs in order to
make troubleshooting more comfortable. This context is shared by all app using
``logging``, transparently.


=======
 Usage
=======

You have two option to send the context to the log system: inject context as
extra fields in records or append context to the each message.

Using filter
============

This method allow to pass fields to JSON formatters, log servers, etc. or use
the extra fields in format string.

.. code-block::

    LOGGING = {
        'version': 1,
        'formatters': {
            'extra': {
                'format': '%(levelname)s %(rid)s %(name)s %(message)s',
            },
        },
        'filters': {
            'context_filter': {
                '()': 'django_context_logging.AddContextFilter',
                'default': {'rid': None},
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'filters': ['context_filter'],
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }

Note three things:

* ``%(rid)`` in format string is for logging rid (for request_id) from our
  context;
* ``django_context_logging.AddContextFilter`` - filter which converts keys from
  context dict to attributes of LogRecord;
* ``'default': {'rid': None}`` - some of our log events could be without
  context for example logs emitted on worker start. All these logs will not be
  recorded due to the lack of 'rid' attribute (in our example) on LogRecord
  instance. To fix this we provide default value for 'rid'.


Using formatter
===============

If you do not want to bother with custom log format and default context values
for a filter - you can use ``django_context_logging.AddContextFormatter``.

.. code-block::

    LOGGING = {
        'version': 1,
        'formatters': {
            'append': {
                '()': 'django_context_logging.AddContextFormatter'
                'format': '%(levelname)s %(name)s %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'append',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }

As you can see in this case we doesn't add any context related fields to a log
format string.  This is because ``django_context_logging.AddContextFormatter``
will append all context information to every log.


Feeding the context
===================

The context class is just a thread local dict. It is used as local registry to
inject shared fields in log records. Here is a full example:

.. code-block::

   from django_context_logging.log import context as log_context


   log_context.push(userId=user.pk)
   # code, log, etc.
   for article in blog.articles:
       with log_context(articleId=article.pk):
           # code, log, ...
   # code, log, etc.
   log_context.pop('userId')


Automatic feeding with middleware
---------------------------------

A middleware is provided to inject extra fields in context. It will also clear
the context after each requests.

.. code-block::

    MIDDLEWARE_CLASSES = [
        'django_context_logging.ExtractRequestContextMiddleware',
        # rest middlewares
    ]

    DJANGO_CONTEXT_LOGGING_EXTRACTOR = lambda request: {'rid': request.GET.getlist('rid')}


Here DJANGO_CONTEXT_LOGGING_EXTRACTOR is a callable which takes
django.http.request.HttpRequest and returns dictionary with extracted context.

**Note:** ExtractRequestContextMiddleware will fail with exception if no
 DJANGO_CONTEXT_LOGGING_EXTRACTOR specified.

 Contributors
 ------------

  * Lev Orekhov `@lorehov <https://github.com/lorehov>`_
  * Étienne BERSAC `@bersace <https://github.com/bersace>`_
