# =============================================================================
# Development helpers in the form of make targets
# =============================================================================
# This file is part of the FSFE Form Server.
#
# Copyright © 2017-2019 Free Software Foundation Europe <contact@fsfe.org>
#
# The FSFE Form Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# The FSFE Form Server is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details <http://www.gnu.org/licenses/>.
# =============================================================================

SOURCE_DIR = fsfe_forms

.DEFAULT_GOAL := help

GREEN  = $(shell tput -Txterm setaf 2)
WHITE  = $(shell tput -Txterm setaf 7)
YELLOW = $(shell tput -Txterm setaf 3)
RESET  = $(shell tput -Txterm sgr0)

HELPME = \
	%help; \
	while(<>) { push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^([a-zA-Z\-]+)\s*:.*\#\#(?:@([a-zA-Z\-]+))?\s(.*)$$/ }; \
	for (sort keys %help) { \
	print "${WHITE}$$_:${RESET}\n"; \
	for (@{$$help{$$_}}) { \
	$$sep = " " x (20 - length $$_->[0]); \
	print "  ${YELLOW}$$_->[0]${RESET}$$sep${GREEN}$$_->[1]${RESET}\n"; \
	}; \
	print "\n"; }

help:
	@perl -e '$(HELPME)' $(MAKEFILE_LIST)
.PHONY: help

virtualenv:  ##@development Set up the virtual environment with the Python dependencies.
	@pipenv install --dev
.PHONY: virtualenv

applyisort:  ##@development Apply a correct Python import sort inline.
	@pipenv run isort
.PHONY: applyisort

flask:  ##@development Run the Flask built-in web server.
	@pipenv run flask run
.PHONY: flask

gunicorn:  ##@development Run the Gunicorn based web server.
	@. ./.env && pipenv run gunicorn --bind $$FLASK_RUN_HOST:$$FLASK_RUN_PORT "$$FLASK_APP:create_app()"
.PHONY: gunicorn

isort:  ##@quality Check the Python source code for import sorting.
	@pipenv run isort --check-only --diff
.PHONY: isort

lint:  ##@quality Check the Python source code for coding standards compliance.
	@pipenv run pylama
.PHONY: lint

pytest:  ##@quality Run the functional tests.
	@pipenv run pytest --cov=$(SOURCE_DIR)
	@pipenv run coverage html
.PHONY: pytest

quality: isort lint pytest  ##@quality Run all quality checks.
.PHONY: quality
