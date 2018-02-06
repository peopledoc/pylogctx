===========
 Changelog
===========

1.9 (2018-02-06)
++++++++++++++++

- Fix nested dict is None when recursive deepupdate


1.8 (2018-02-06)
++++++++++++++++

- Fix update_one to deepupdate
- Celery: Add arg and kwargs from method `before_call` and `after_call`
  of `LoggingTask`


1.7 (2018-01-17)
++++++++++++++++

- Fix deepupdate when target is not the same from the src


1.6 (2018-01-03)
++++++++++++++++

- Fix update context from celery loggingTask


1.5 (2018-01-03)
++++++++++++++++

- Extended nested dictionary when key already exist during context update (#19)
- Celery: Manage context logs when task call another task


1.4 (2017-12-21)
++++++++++++++++

- New method to update one object in adapter with custom parameters::

        log_context.update_one(Request, p1=True, p2=...)

        # Or
        with log_context.context.cm_update_one(Request, p1=True, p2=...):
           ...


1.3 (2017-12-13)
++++++++++++++++

- Support Celery 4
- Support python 3.5
