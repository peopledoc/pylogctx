# About

`django_context_logging` is a library for adding request context to logs.
Typical usage is for adding some request_id to all logs in order to make troubleshooting
more comfortable.


# Usage

First enable middleware for storing request context.

    MIDDLEWARE_CLASSES = [
        'django_context_logging.ExtractRequestContextMiddleware',
        # rest middlewares
    ]
    
    DJANGO_CONTEXT_LOGGING_EXTRACTOR = lambda request: {'rid': request.GET.getlist('rid')}


Here DJANGO_CONTEXT_LOGGING_EXTRACTOR is a callable which takes django.http.request.HttpRequest
and returns dictionary with extracted context.

**Note:** ExtractRequestContextMiddleware will fail with exception if no DJANGO_CONTEXT_LOGGING_EXTRACTOR specified.

Now it is possible to configure logging in one of two possible ways.

## Using filter

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(process)d %(rid)s %(name)s %(message)s'
            },
        },
        'filters': {
            'context_filter': {
                '()': 'django_context_logging.AddContextFilter', 
                'default': {'rid': None}
            }
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/path/to/django/debug.log',
                'filters': ['context_filter']
            },
        },
        'loggers': {
            '': {
                'handlers': ['file'],
                'level': 'DEBUG'
            },
        }
    }

Note three things:

  * `%(rid)` in format string is for logging rid (for request_id) from our context;
  * `django_context_logging.AddContextFilter` - filter which converts keys from context dict to attributes of LogRecord;
  *  `'default': {'rid': None}` - some of our log events could be without context for example logs emitted on worker start. All these logs will not be recorded due to the lack of 'rid' attribute (in our example) on LogRecord instance. To fix this we provide default value for 'rid'.  

## Using formatter

If you do not want to bother with custom log format and default context values for a filter - you can use `django_context_logging.AddContextFormatter`.

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                '()': 'django_context_logging.AddContextFormatter'
                'format': '%(levelname)s %(asctime)s %(process)d %(name)s %(message)s'
            },
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/path/to/django/debug.log',
            },
        },
        'loggers': {
            '': {
                'handlers': ['file'],
                'level': 'DEBUG'
            },
        }
    }

As you can see in this case we doesn't add any context related fields to a log format string.
This is because `django_context_logging.AddContextFormatter` will append all context information to every log. 
