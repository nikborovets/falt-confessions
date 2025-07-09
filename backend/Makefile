SHELL := /bin/sh

###############################################################################
# Discover the target environment and config:
# Discovery is based on "ENV" environment variable that should be passed with
# every make command. For convenience "dev" environment is the default
# (so ENV var can be omitted). Still, for other environments you need to
# explicitly call the make command like this: "ENV=stage make stuff".

ifeq ($(ENV),)
	include .env-dev
else ifeq ($(ENV),dev)
	include .env-dev
else ifeq ($(ENV),stage)
	include .env-stage
else ifeq ($(ENV),prod)
	include .env
endif

###############################################################################

install:
	poetry install

test:
	poetry run pytest src/tests

lint:
	poetry run pre-commit run --all-files

check: test
	poetry run pre-commit run --all-files

hooks:
	poetry run pre-commit install

dev-docker-run-postgres:
	docker compose up -d postgres

dev-init:
	poetry install

dev-run-server:
	docker compose up -d fastapi

dev-test:
	docker exec -it fastapi sh -c "poetry run pytest tests"

dev-migrate:
	docker exec -it fastapi sh -c "poetry run alembic upgrade head"
