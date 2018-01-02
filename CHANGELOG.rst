Changelog
---------


1.4 (unreleased)
++++++++++++++++

- Extended nested dictionary when key already exist during context update (#19)


1.3 (2017-12-21)
++++++++++++++++

- New method to update one object in adapter with custom parameters::

        log_context.update_one(Request, p1=True, p2=...)

        # Or
        with log_context.context.cm_update_one(Request, p1=True, p2=...):
           ...


1.2 (2017-12-13)
++++++++++++++++

- Support Celery 4
- Support python 3.5
