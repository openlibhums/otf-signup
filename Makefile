unexport NO_DEPS
DB_NAME ?= signup
DB_HOST=signup-postgres
DB_VENDOR ?= postgres
DB_PORT=5432
DB_USER=signup
DB_PASSWORD=signup
DB_VOLUME=postgres-data
CLI_COMMAND=psql --username=$(DB_USER) $(DB_NAME)

ifdef VERBOSE
	_VERBOSE=--verbose
endif

export DB_VENDOR
export DB_HOST
export DB_PORT
export DB_NAME
export DB_USER
export DB_PASSWORD
SUFFIX ?= $(shell python -c "from time import time; print(hex(int(time()*10000000))[2:])")
SUFFIX := ${SUFFIX}
DATE := `date +"%y-%m-%d"`

all: install
help:		## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
run:	## Run dev web server in attached mode. If NO_DEPS is not set, runs all dependant services detached.
	docker-compose --project-directory $(PWD) $(_VERBOSE) -f dockerfiles/docker-compose.yml run $(NO_DEPS) --rm --service-ports signup  $(entrypoint)
command:	## Run project in a container and pass through a django command passed as the CMD environment variable
	docker-compose --project-directory $(PWD) -f dockerfiles/docker-compose.yml run $(NO_DEPS) --rm signup $(CMD)
install:	## Run the first setup tasks
	bash -c "make command CMD=migrate"
rebuild:	## Rebuild the project docker image.
	docker-compose --project-directory $(PWD) -f dockerfiles/docker-compose.yml build  --no-cache signup
shell:		## Runs the project service and starts an interactive bash process instead of the webserver
	docker-compose --project-directory $(PWD) -f dockerfiles/docker-compose.yml run --entrypoint=/bin/bash --rm signup
attach:		## Runs an interactive bash process within the currently running project container
	docker exec -ti `docker ps -q --filter 'name=signup'` /bin/bash
db-client:	## runs the database CLI client interactively within the database container as per the value of DB_VENDOR
	docker exec -ti `docker ps -q --filter 'name=signup-postgres'` $(CLI_COMMAND)
uninstall:	## Removes all project related docker containers, docker images and database volumes
	@bash -c "sudo rm -rf volumes/postgres-data"
	@bash -c "docker rm -f `docker ps --filter 'name=signup*' -aq` >/dev/null 2>&1 | true"
	@bash -c "docker rmi `docker images -q signup*` >/dev/null 2>&1 | true"
	@echo " Project has been uninstalled"
check:		## Runs project test suit
	bash -c "make command CMD=test"
