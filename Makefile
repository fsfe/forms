# =============================================================================
# Development helpers in the form of make targets
# =============================================================================
# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

SOURCE_DIR = fsfe_forms
# Files/dirs to be checked by pylama/isort
QUALITY_TARGETS = $(SOURCE_DIR) tests/* *.py

export FLASK_SKIP_DOTENV = 1
export FLASK_APP = ${SOURCE_DIR}
export FLASK_ENV = development
export FLASK_RUN_HOST = localhost
export FLASK_RUN_PORT = 8080

.DEFAULT_GOAL := help

GREEN  = $(shell tput -Txterm setaf 2)
WHITE  = $(shell tput -Txterm setaf 7)
YELLOW = $(shell tput -Txterm setaf 3)
RESET  = $(shell tput -Txterm sgr0)

COMPOSE := docker compose

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

dev: ##@development Start all containers and show their logs.
	@USER_ID=$${USER_ID:-`id -u`} GROUP_ID=$${GROUP_ID:-`id -g`} docker compose -f docker-compose.dev.yml up --build --force-recreate
.PHONY: dev

dev.up: ##@development Start all containers and detach.
	@USER_ID=$${USER_ID:-`id -u`} GROUP_ID=$${GROUP_ID:-`id -g`} docker compose -f docker-compose.dev.yml up --build --force-recreate --detach
.PHONY: dev.up

dev.down: ##@development Stop all containers.
	@$(COMPOSE) -f docker-compose.dev.yml down
.PHONY: dev.down

dev.kill: ##@development Kill and subsequently remove all containers.
	@$(COMPOSE) -f docker-compose.dev.yml kill
	@$(COMPOSE) -f docker-compose.dev.yml rm --force --stop -v
.PHONY: dev.kill

dev.logs: ##@development Show logs of running containers.
	@$(COMPOSE) -f docker-compose.dev.yml logs --timestamps --follow
.PHONY: dev.logs

toolshell:  ##@development Start a shell in which the command line tools can be run.
	@docker exec -it forms /bin/sh -c 'PATH=src/bin:$$PATH bash'
.PHONY: toolshell

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
	@pipenv run isort --check --diff $(QUALITY_TARGETS)
.PHONY: isort

pylama:  ##@quality Check the Python source code for coding standards compliance.
	@pipenv run pylama
.PHONY: pylama

pytest:  ##@quality Run the functional tests.
	@pipenv run pytest --cov=$(SOURCE_DIR) tests
.PHONY: pytest

reqs: ##@quality Ensure requirements.txt files are in sync with Pipfiles
	@pipenv requirements --dev > requirements_all.txt && pipenv requirements > requirements.txt
.PHONY: reqs

quality: isort pylama pytest  ##@quality Run all quality checks.
.PHONY: quality
