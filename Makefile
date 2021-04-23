.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

format: ## apply black code formatter
	black .

lint: ## check style with flake8
	flake8 esparto tests

mypy: ## check type hints
	mypy esparto tests

test: ## run tests quickly with the default Python
	pytest
	python -m tests.check_package_version

test-all: ## run tests on every Python version with tox
	tox --skip-missing-interpreters
	python -m tests.check_package_version

coverage: ## check code coverage quickly with the default Python
	coverage run --source esparto -m pytest
	coverage report -m
	coverage html
	# $(BROWSER) htmlcov/index.html

docstrings: ## generate google format docstrings
	pyment esparto -o google -w

docs: ## generate Sphinx HTML documentation, including API docs
	mkdocs clean
	mkdocs build

servedocs: ## compile the docs watching for changes
	mkdocs serve -a "`hostname -I | xargs`:8000"

release: dist ## package and upload a release
	poetry publish

dist: clean ## builds source and wheel package
	poetry build
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	poetry install
