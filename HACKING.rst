#####################
 Hacking on pylogctx
#####################


Releasing a new version
=======================

The root ``Makefile`` ease releasing and uploading a new version of pylogctx.
Here is the release checklist:

- You must have write access to ``master`` on upstream repository.
- You must have upload access to https://pypi.python.org/pypi/pylogctx.

Here are steps to release:

- Ensure the new version has an entry in CHANGELOG_.
- Increment version in ``setup.py``.
- Run ``make release`` to create commit and tag.
- Now run ``make upload`` to create tarball and wheel. You
