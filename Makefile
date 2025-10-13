.PHONY: install test clean

SHELL			:= /bin/bash

PRINTF			:= printf
RM			:= rm
TOUCH			:= touch
FIND			:= find
GREP			:= grep

VENV 			:= .venv
VENV_INSTALLED_STAMP	:= .venv_installed_stamp
PYTHON 			:= $(VENV)/bin/python3
PIP			:= $(VENV)/bin/pip
PYTEST			:= $(VENV)/bin/pytest

PROJ_FILES		:= $(shell git ls-files)

# Keywords to filter tests on (defaults to everything)
TESTS			?= ""
COVERAGE_ARGS		:= --cov=$(PKG_NAME) --cov-report=term-missing
TEST_ARGS		:= ""

# The IOGEN_LOG environment variable can be used to overide the default log level
IOGEN			:= IOGEN_LOG=$(IOGEN_LOG) $(PYTHON) -m io_gen
EXAMPLE_YAML		:= examples/arty-z7-20.yaml

help:
	@$(PRINTF) '%s\n' "Available targets:"
	@$(PRINTF) '%-16s %s\n' "  help" "This help menu"
	@$(PRINTF) '%-16s %s\n' "  test" "Run entire test suite"
	@$(PRINTF) '%-16s %s\n' "  debug" "Run entire test suite, with PDB and output directed to console"
	@$(PRINTF) '%-16s %s\n' "  coverage" "Run tests with coverage"
	@$(PRINTF) '%-16s %s\n' "  check-ascii" "Search the source tree for non-ASCII characters"
	@$(PRINTF) '\n'
	@$(PRINTF) '%s\n' "Development targets:"
	@$(PRINTF) '%-16s %s\n' "  run-validate" "Schema validate"

$(VENV_INSTALLED_STAMP): requirements.txt
	@$(PRINTF) '%s\n' "Initializing virtual environment"
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(TOUCH) $(VENV_INSTALLED_STAMP)

run-validate: $(VENV_INSTALLED_STAMP)
	$(IOGEN) $(VERBOSE) validate --input $(EXAMPLE_YAML)

run-xdc: $(VENV_INSTALLED_STAMP)
	$(IOGEN) emit_xdc --input $(EXAMPLE_YAML)

run-vhdl: $(VENV_INSTALLED_STAMP)
	$(IOGEN) emit_vhdl --input $(EXAMPLE_YAML)

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

