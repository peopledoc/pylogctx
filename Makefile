VERSION = $(shell python setup.py --version)
UPSTREAM=git@github.com:peopledoc/pylogctx.git

default:

release:
	python setup.py egg_info
	: Ensure Changelog entry
	grep -q $(VERSION) CHANGELOG.rst
	: Pin date of release
	sed -i '/$(VERSION)/s/unreleased/$(shell date +%Y-%m-%d)/' CHANGELOG.rst
	: Commit, tag and push setup.py and Changelog
	git commit setup.py CHANGELOG.rst -m "Version $(VERSION)"
	git tag $(VERSION)
	git push $(UPSTREAM)
	git push $(UPSTREAM)
	@echo Now upload with make upload

upload:
	: Ensure we build from tag
	git describe --exact-match --tags
	python3 setup.py sdist bdist_wheel --universal upload -r pypi


test:
	python setup.py test
