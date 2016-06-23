import itertools
import logging
import threading


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
        """
        self.data.update(fields)

        for object_ in objects:
            if not object_:
                # You can safely pass None, it will be ignored.
                continue

            self.data.update(adapt(object_))

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
        return dict(self.items())

    def items(self):
        # Ensure thread local data is ready
        self.data
        # Squash all dict in stack
        return itertools.chain(*[d.items() for d in self._stack])

    def __call__(self, *objects, **fields):
        return ContextManager(self, *objects, **fields)


class ContextManager(object):
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
        context_str = u' '.join([
            u'{}:{}'.format(k, v) for k, v in context.items()
        ])
        return u'{msg} {context}'.format(msg=msg, context=context_str)


_adapter_mapping = {}


class AdapterNotFound(Exception):
    pass


def log_adapter(class_):
    def decorator(callable_):
        _adapter_mapping[class_] = callable_
        return callable_
    return decorator


def adapt(object_):
    for class_ in type(object_).__mro__:
        try:
            adapter = _adapter_mapping[class_]
            break
        except KeyError:
            continue
    else:
        raise AdapterNotFound("Can't log object of type %r" % type(object_))
    return adapter(object_)


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
