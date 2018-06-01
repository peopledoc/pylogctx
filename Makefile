VERSION = $(shell python setup.py --version)
UPSTREAM=git@github.com:peopledoc/pylogctx.git

default:

clean: clean-build clean-pyc

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	find . -name '__pycache__' -exec rm -rf {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

release: clean
	tox -e release

upload:
	: Ensure we build from tag
	git describe --exact-match --tags
	python3 setup.py sdist bdist_wheel --universal upload -r pypi

test:
	python setup.py test
