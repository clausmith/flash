# http://www.heavybit.com/library/blog/opinionated-tour-of-testing-tools/
# https://github.com/bear/tenki

.PHONY: help install-hook clean info update server init upgrade migrate seed shell restart
SHELL = /bin/bash

help:
	@echo "This project assumes that an active Python virtualenv is present."
	@echo "The following targets are available:"
	@echo "  update        update python dependencies"
	@echo "  clean         remove unwanted files"
	@echo "  lint          flake8 lint check"
	@echo "  test          run unit tests"
	@echo "  integration   run integration tests"
	@echo "  ci            run unit, integration and codecov"
	@echo "  all           refresh and run all tests and generate coverage reports"
	@echo "  server        start the Flask server"

update:
	pip install -U pip
	pip install -Ur requirements.txt

clean:
	python manage.py clean

lint: clean
	flake8 --exclude=env . > violations.flake8.txt

test:   clean
	python manage.py test

integration:
	python manage.py integration

webtest: docker-start
	$(eval DRIVER_IP := $(shell ./wait_for_ip.sh))
	DRIVER_IP=$(DRIVER_IP) python manage.py webtest
	docker-compose stop

coverage:
	@coverage run --source=app manage.py test
	@coverage html
	@coverage report

ci: info clean coverage test integration webtest
	CODECOV_TOKEN=`cat .codecov-token` codecov

docker-build:
	docker-compose build
	docker-compose pull
	docker-compose rm -f

docker-start:
	docker-compose up -d

init-db:
	flask db init

upgrade:
	flask db upgrade

migrate:
	flask db migrate

seed:
	flask seed

shell:
	flask shell

server:
	flask run

docker-restart:
	docker-compose restart

all: update integration coverage webtest

info:
	@python --version
	@pip --version
	@virtualenv --version
