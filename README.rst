| |GitHub| |BSD| |CI| |PyPI|

########################
 Python Logging Context
########################

``pylogctx`` is a library for enriching each logs records from a context.
Typical usage is for adding some ``request_id`` to all logs in order to make
troubleshooting more comfortable. This context is shared by all piece of code
using ``logging``, transparently.

.. code-block::

    import logging.config

    from pylogctx import context as log_context


    logging.config.dictConfig({
        'formatters': {'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': "%(asctime)s %(name)s %(levelname)s %(message)s",
        }},
        'filters': {'context': {
            '()': 'pylogctx.AddContextFilter',
        }},
        'handlers': {'console': {
            'class': 'logging.StreamHandler',
            'filters': ['context'],
            'formatter': 'json',
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    })


    logger = logging.getLogger(__name__)


    def mycode(request, ticket_id):
        # push new fields
        log_context.update(requestId=uuid.uuid4())
        myticket = get_object_or_404(models.Ticket, pk=ticket_id)

        # push objects, they will be adapted to log fields
        log_context.update(myticket):

        # Log as usual
        logger.info("Working on %r", myticket)

        for comment in myticket.comments:
            # A context manager allow to push and pop fields
            with log_context(comment):
                logger.info("Working on comment %r", comment)
                # code, use external libs, etc.

        # Don't forget to clear the context for the next request. Use the
        # middleware to have it clean.
        log_context.clear()


The output looks like::

     {'loggerName': 'package.module', 'levelname': 'INFO', 'message': 'Working on <Ticket #1>', 'ticketId': 1, 'requestId': 'c5521138-031a-4da6-b9db-c9eda3e090f1'}
     {'loggerName': 'package.module', 'levelname': 'INFO', 'message': 'Working on comment <Comment #4>', 'ticketId': 1, 'ticketCommentId': 4, 'requestId': 'c5521138-031a-4da6-b9db-c9eda3e090f1'}
     {'loggerName': 'package.module', 'levelname': 'INFO', 'message': 'Working on comment <Comment #5>', 'ticketId': 1, 'ticketCommentId': 5, 'requestId': 'c5521138-031a-4da6-b9db-c9eda3e090f1'}
     {'loggerName': 'package.module', 'levelname': 'INFO', 'message': 'Working on comment <Comment #78>', 'ticketId': 1, 'ticketCommentId': 78, 'requestId': 'c5521138-031a-4da6-b9db-c9eda3e090f1'}
     {'loggerName': 'package.module', 'levelname': 'INFO', 'message': 'Working on comment <Comment #9>', 'ticketId': 1, 'ticketCommentId': 9, 'requestId': 'c5521138-031a-4da6-b9db-c9eda3e090f1'}
     {'loggerName': 'package.module', 'levelname': 'INFO', 'message': 'Working on <Ticket #890>', 'ticketId': 890, 'requestId': 'c64aaae7-049b-4a02-929b-2d0ac9141f5c'}
     {'loggerName': 'package.module', 'levelname': 'INFO', 'message': 'Working on comment <Comment #80>', 'ticketId': 890, 'ticketCommentId': 80, 'requestId': 'c64aaae7-049b-4a02-929b-2d0ac9141f5c'}


Install it with your favorite python package installer::

   $ pip install pylogctx


There is a few helpers for Celery_ and Django_ projects. See USAGE_ for details!


Contributors
============

Do you want py3 support or other nice improvements ? Join us to make log
rocking better!

* Lev Orekhov `@lorehov <https://github.com/lorehov>`_
* Étienne BERSAC `@bersace <https://github.com/bersace>`_


.. |BSD| image:: https://img.shields.io/pypi/l/pylogctx.svg?maxAge=2592000
   :target: https://github.com/novafloss/pylogctx/blob/master/LICENSE
   :alt: BSD Licensed

.. |CI| image:: https://travis-ci.org/peopledoc/pylogctx.svg?style=shield
   :target: https://travis-ci.org/peopledoc/pylogctx
   :alt: CI Status

.. |GitHub| image:: https://img.shields.io/github/stars/novafloss/pylogctx.svg?label=GitHub%20stars
   :target: https://github.com/novafloss/pylogctx
   :alt: GitHub homepage

.. |PyPI| image:: https://img.shields.io/pypi/v/pylogctx.svg
   :target: https://pypi.python.org/pypi/pylogctx
   :alt: Version on PyPI

.. _Celery: http://www.celeryproject.org/
.. _Django: https://www.djangoproject.com/
.. _USAGE: https://github.com/novafloss/pylogctx/blob/master/USAGE.rst
