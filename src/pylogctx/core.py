from __future__ import unicode_literals

import itertools
import logging
import threading

from .helpers import deepupdate


_log = logging.getLogger(__name__)


class Context(threading.local):
    @property
    def data(self):
        # Since we are local, the property is not initialize upon init on
        # object (which is shared) but on first access *in* thread.
        try:
            self._stack
        except AttributeError:
            self._stack = [{}]
        return self._stack[0]

    def clear(self):
        """
        Drop all records
        """
        self.data.clear()

    def update(self, *objects, **fields):
        """
        Push records in context.

        `objects`: Instance of few/an object(s), usually a model object.

        `fields`: Custom fields to push in context.

        Usage:
        .. code-block:: python

            log_context.update(Request, Task)
            log_context.update(Request, userId=2, articleId=4)
        """
        deepupdate(self.data, fields)

        for object_ in objects:
            if not object_:
                # You can safely pass None, it will be ignored.
                continue
            self.update_one(object_)

    def update_one(self, object_, **adapter_kw):
        """
        Push records from object in context with adapter kwargs

        `object_`: Instance of an object, usually a model object.

        `adapter_kw`: Pass extra kwargs to object.

        Usage:
        .. code-block:: python

            log_context.update(Request)
            log_context.update(Request, full_logs=True, display=True, ...)
        """
        deepupdate(self.data, adapt(object_, **adapter_kw))

    def remove(self, *keys):
        """
        Drop records from context.

        Inexistant records are ignored.
        """
        return self.remove_many(keys)

    def remove_many(self, keys):
        for k in keys:
            try:
                self.data.pop(k)
            except KeyError:
                pass

    def as_dict(self):
        """
        Return the context as a dict.
        """
        # Ensure thread local data is ready
        self.data

        items = {}
        # Squash all dict in stack and reverse order because
        # the first values in stack are the last inserted values and we need
        # to override values with the last inserted
        for d in reversed(self._stack):
            deepupdate(items, d)
        return items

    def items(self):
        return itertools.chain(*[self.as_dict().items()])

    def __call__(self, *objects, **fields):
        return UpdateContextManager(self, *objects, **fields)

    def cm_update_one(self, object_, **adapter_kw):
        return UpdateOneContextManager(self, object_, **adapter_kw)


class UpdateContextManager(object):
    def __init__(self, log_context, *objects, **fields):
        self.log_context = log_context
        self.objects = objects
        self.fields = fields

    def __enter__(self):
        # Ensure thread local data is ready
        self.log_context.data
        self.log_context._stack.insert(0, {})
        self.log_context.update(*self.objects, **self.fields)

    def __exit__(self, exc_type, exc_value, traceback):
        self.log_context._stack.pop(0)


class UpdateOneContextManager(object):
    def __init__(self, log_context, object_=None, **adapter_kw):
        self.log_context = log_context
        self.object_ = object_
        self.adapter_kw = adapter_kw

    def __enter__(self):
        # Ensure thread local data is ready
        self.log_context.data
        self.log_context._stack.insert(0, {})
        self.log_context.update_one(self.object_, **self.adapter_kw)

    def __exit__(self, exc_type, exc_value, traceback):
        self.log_context._stack.pop(0)


context = Context()


class AddContextFilter(logging.Filter):
    def __init__(self, name='', default=None):
        super(AddContextFilter, self).__init__(name)
        self.default = default or {}

    def filter(self, record):
        fields = dict(self.default, **context.as_dict())
        record.__dict__.update(fields)
        return True


class ExcInfoFilter(logging.Filter):
    def filter(self, record):
        record.exc_info = None
        return True


class AddContextFormatter(logging.Formatter):
    def format(self, record):
        msg = super(AddContextFormatter, self).format(record)
        context_str = ' '.join([
            '{}:{}'.format(k, v) for k, v in context.items()
        ])
        return '{msg} {context}'.format(msg=msg, context=context_str)


_adapter_mapping = {}


class AdapterNotFound(Exception):
    pass


def log_adapter(class_):
    def decorator(callable_):
        _adapter_mapping[class_] = callable_
        return callable_
    return decorator


def adapt(object_, **kwargs):
    for class_ in object_.__class__.__mro__:
        try:
            adapter = _adapter_mapping[class_]
            break
        except KeyError:
            continue
    else:
        raise AdapterNotFound("Can't log object of type %r" % type(object_))
    return adapter(object_, **kwargs)


class LazyAccessor(object):
    def __init__(self, instance, attrname):
        self.instance = instance
        self.attrname = attrname

    def get(self):
        return getattr(self.instance, self.attrname)

    def __unicode__(self):
        return unicode(self.get())

    def __str__(self):
        return str(self.get())

    def __repr__(self):
        return repr(self.get())
