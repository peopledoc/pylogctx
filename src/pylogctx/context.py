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

    def update(self, **fields):
        """
        Push records in context.
        """
        self.data.update(fields)

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
    def __init__(self, log_context, **fields):
        self.log_context = log_context
        self.fields = fields

    def __enter__(self):
        # Ensure thread local data is ready
        self.log_context.data
        self.log_context._stack.insert(0, {})
        self.log_context.update(**self.fields)

    def __exit__(self, exc_type, exc_value, traceback):
        self.log_context._stack.pop(0)


context = Context()
