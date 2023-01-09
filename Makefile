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
	@USER_ID=$${USER_ID:-`id -u`} GROUP_ID=$${GROUP_ID:-`id -g`} $(COMPOSE) -f docker-compose.dev.yml up --build --force-recreate
.PHONY: dev

dev.up: ##@development Start all containers and detach.
	@USER_ID=$${USER_ID:-`id -u`} GROUP_ID=$${GROUP_ID:-`id -g`} $(COMPOSE) -f docker-compose.dev.yml up --build --force-recreate --detach
.PHONY: dev.up

dev.down: ##@development Stop all containers.
	@USER_ID=$${USER_ID:-`id -u`} GROUP_ID=$${GROUP_ID:-`id -g`} $(COMPOSE) -f docker-compose.dev.yml down
.PHONY: dev.down

dev.kill: ##@development Kill and subsequently remove all containers.
	$(COMPOSE) -f docker-compose.dev.yml kill
	$(COMPOSE) -f docker-compose.dev.yml rm --force --stop -v
.PHONY: dev.kill

dev.logs: ##@development Show logs of running containers.
	$(COMPOSE) -f docker-compose.dev.yml logs --timestamps --follow
.PHONY: dev.logs

toolshell:  ##@development Start a shell in which the command line tools can be run.
	@docker exec -it forms /bin/sh -c 'PATH=src/bin:$$PATH bash'
.PHONY: toolshell

isort.forms: ##@quality-control Run isort in `forms-quality` container.
	@echo "=== [back] Checking for the correct order of imports ==="
	@docker exec -it forms-quality /bin/sh -c "cd src && isort . --check --diff"
	@echo "=== [back] Your imports are properly sorted ==="
.PHONY: isort.forms

isort.all: isort.forms ##@quality-control Run isort in all modules.

lint.forms: ##@quality-control Run linter in `forms-quality` container.
	@echo "=== [back] Checking the formatting ==="
	@docker exec -it forms-quality /bin/sh -c "pylama -i E216"
	@echo "=== [back] Code is properly formatted ==="
.PHONY: lint.forms

test.forms: ##@quality-control Run pytest in `forms-quality` container.
	@docker exec -it forms-quality /bin/sh -c "cd src && pytest --cov=fsfe_forms"
	@docker exec -it forms-quality /bin/sh -c "cd src && coverage html"
.PHONY: text.forms

test.all: test.forms ##@quality-control Run pytest in all modules.

qc.forms: isort.forms lint.forms test.forms ##@quality-control Run all quality control tools in `forms` container.
qc.all: qc.forms ##@quality-control Run all quality control tools in all containers.
