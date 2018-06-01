import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

version = '1.12'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['tests/']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='pylogctx',
    version=version,
    description='Adding context to log records',
    long_description=README,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='logging context logging django',
    author="Lev Orekhov",
    author_email="lev.orekhov@gmail.com",
    url="https://github.com/novafloss/pylogctx",
    license="BSD",
    package_dir={'': 'src'},
    packages=['pylogctx'],
    cmdclass={'test': PyTest},
    include_package_data=True,
    zip_safe=False,
    tests_require=[
        'django>=1.11,<2' if sys.version_info[0] == 2 else 'django>=1.11',
        'mock>=2.0.0',
        'pytest>=2.9.0',
        'celery',
        'six'
    ],
)
