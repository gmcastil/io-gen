UNAME			:= $(shell uname)

SHELL			:= /bin/bash

ifeq ($(UNAME),Darwin)
	GREP := ggrep
else
	GREP := grep
endif

PRINTF			:= builtin printf
RM			:= rm
TOUCH			:= touch
FIND			:= find

VENV 			:= .venv
VENV_INSTALLED_STAMP	:= .venv_installed_stamp
PYTHON 			:= $(VENV)/bin/python3
PIP			:= $(VENV)/bin/pip
PYTEST			:= $(VENV)/bin/pytest

PKG_NAME		:= io_gen

PROJ_FILES		:= $(shell git ls-files)

# Keywords to filter tests on with `-k $(TESTS)` (default is all of them)
TESTS			?= ""

COVERAGE_ARGS		:= --cov=$(PKG_NAME) --cov-report=term-missing
TEST_ARGS		:= ""

.PHONY: install test clean

help:
	@$(PRINTF) '%s\n' "Available targets:"
	@$(PRINTF) '%-16s %s\n' "  help" "This help menu"
	@$(PRINTF) '%-16s %s\n' "  test" "Run entire test suite"
	@$(PRINTF) '%-16s %s\n' "  debug" "Run entire test suite, with PDB and output directed to console"
	@$(PRINTF) '%-16s %s\n' "  coverage" "Run tests with coverage"
	@$(PRINTF) '%-16s %s\n' "  check-ascii" "Search the source tree for non-ASCII characters"

$(VENV_INSTALLED_STAMP): requirements.txt
	@$(PRINTF) '%s\n' "Initializing virtual environment"
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(TOUCH) $(VENV_INSTALLED_STAMP)

test: $(VENV_INSTALLED_STAMP)
	@$(PYTHON) -m pytest -k $(TESTS) $(TEST_ARGS)

debug: $(VENV_INSTALLED_STAMP)
	$(PYTHON) -m pytest -k $(TESTS) -vv -s --pdb

coverage: $(VENV_INSTALLED_STAMP)
	@$(PYTHON) -m pytest $(COVERAGE_ARGS)

check-venv: $(VENV_INSTALLED_STAMP)
	@$(PYTHON) -m site
	@$(PRINTF) '%s\n' "Executable: $(PYTHON)"
	@$(PRINTF) '%s' "Sys.path: "
	@$(PYTHON) -c "import sys; from pprint import pprint; pprint(sys.path)"

clean-pyc:
	$(FIND) . -type f -iname '*.py[co]' -delete
	$(FIND) . -type d -iname '__pycache__' -delete
	$(RM) -rf .pytest_cache

check-ascii:
	@$(PRINTF) '%s\n' "Checking for non-ASCII characters..."
	@LC_ALL=C $(GREP) --color='always' -Pn "[^\x00-\x7F]" $(PROJ_FILES) || $(PRINTF) 'OK\n'

clean: clean-pyc
	$(RM) -rf $(VENV)
	$(RM) -f $(VENV_INSTALLED_STAMP)
	$(RM) -f .coverage
