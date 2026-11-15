#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = Santolina_tutor
PYTHON_VERSION = 3.12
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python dependencies
.PHONY: requirements
requirements:
	uv sync
	



## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Run only the copilot tests (standard library only, no model or M3Kang data needed)
.PHONY: test-copilot
test-copilot:
	python3 -m unittest tests.test_pipeline -v


## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	ruff format --check
	ruff check

## Serve the MkDocs site with live reload (http://127.0.0.1:8001)
.PHONY: docs-serve
docs-serve:
	NO_MKDOCS_2_WARNING=1 uv run --group docs mkdocs serve

## Build the MkDocs site into site/ (ignored by Git)
.PHONY: docs-build
docs-build:
	NO_MKDOCS_2_WARNING=1 uv run --group docs mkdocs build

## Check the docs review ledger and print the status table
.PHONY: docs-status
docs-status:
	uv run --group docs python .claude/skills/docs-review/scripts/docs_status.py check
	uv run --group docs python .claude/skills/docs-review/scripts/docs_status.py table

## Start the teacher app (http://127.0.0.1:8010)
.PHONY: teacher
teacher:
	uv run --group teacher python -m teacher_app serve

## Run all the tests: copilot, board data contract, student app, teacher app
.PHONY: test
test:
	uv run --group teacher pytest

## Format source code with ruff
.PHONY: format
format:
	ruff check --fix
	ruff format





## Set up Python interpreter environment
.PHONY: create_environment
create_environment:
	uv venv --python $(PYTHON_VERSION)
	@echo ">>> New uv virtual environment created. Activate with:"
	@echo ">>> Windows: .\\\\.venv\\\\Scripts\\\\activate"
	@echo ">>> Unix/macOS: source ./.venv/bin/activate"
	



#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Make dataset
.PHONY: data
data: requirements
	$(PYTHON_INTERPRETER) santolina_tutor/dataset.py


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
