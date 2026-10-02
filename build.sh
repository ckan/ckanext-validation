#!/bin/sh

set -e

BASEDIR=$(dirname $0)
. $BASEDIR/.env
export LAGOON_LOCALDEV_URL=http://$PROJECT.docker.amazee.io

# derive versions from CKAN version
export CKAN_VERSION=${CKAN_VERSION:-2.11}
PYTHON=python3
PYTHON_VERSION=py3
SOLR_VERSION=9
if [ "$CKAN_VERSION" = "2.10" ]; then
    SOLR_VERSION=8
fi
export SOLR_VERSION

# pre-flight checks
export DOCTOR_CHECK_DB=${DOCTOR_CHECK_DB:-1}
export DOCTOR_CHECK_TOOLS=${DOCTOR_CHECK_TOOLS:-1}
export DOCTOR_CHECK_PORT=${DOCTOR_CHECK_PORT:-0}
export DOCTOR_CHECK_PYGMY=${DOCTOR_CHECK_PYGMY:-1}
export DOCTOR_CHECK_CLI=${DOCTOR_CHECK_CLI:-0}
export DOCTOR_CHECK_SSH=${DOCTOR_CHECK_SSH:-0}
export DOCTOR_CHECK_WEBSERVER=${DOCTOR_CHECK_WEBSERVER:-0}
export DOCTOR_CHECK_BOOTSTRAP=${DOCTOR_CHECK_BOOTSTRAP:-0}

configure_docker () {
    # Generate Docker and Docker Compose configuration files.
    title "Generating CKAN $CKAN_VERSION configuration for Docker Compose..."
    # Remove lines containing '###'.
    # Uncomment lines containing '##'.
    sed -e "/###/d" docker-compose-template.yml | sed -e "s/##//" > docker-compose.yml
    # Pull the latest images.
    pull

    sed "s|{CKAN_VERSION}|$CKAN_VERSION|g" .docker/Dockerfile-template.ckan \
        | sed "s|{CKAN_GIT_VERSION}|$CKAN_GIT_VERSION|g" \
        | sed "s|{CKAN_GIT_ORG}|$CKAN_GIT_ORG|g" \
        | sed "s|{PYTHON_VERSION}|$PYTHON_VERSION|g" \
        | sed "s|{SOLR_VERSION}|$SOLR_VERSION|g" \
        | sed "s|{PYTHON}|$PYTHON|g" \
        > .docker/Dockerfile.ckan
}

# Docker commands.
build () {
    # Build or rebuild project.
    title "Building project"
    configure_docker
    pre_flight
    clean
    build_network
    up --build --force-recreate
    title "Build complete"
    info
}

build_network () {
    # Ensure that the amazeeio network exists.
    title "Creating amazeeio Docker network"
    docker network prune -f > /dev/null
    docker network inspect amazeeio-network > /dev/null || docker network create amazeeio-network
}

info () {
    # Print information about this project.
    line "Project                  : " ${PROJECT}
    line "Site local URL           : " ${LAGOON_LOCALDEV_URL}
    line "DB port on host          : " $(docker port $(docker compose ps -q postgres) 5432 | cut -d : -f 2)
    line "Solr port on host        : " $(docker port $(docker compose ps -q solr) 8983 | cut -d : -f 2)
    line "Mailhog URL              : " http://mailhog.docker.amazee.io/
}

up () {
    # Build and start Docker containers.
    title "Building and starting Docker containers"
    docker compose up -d "$@"
    echo "Initialising database schema"
    cli '"${APP_DIR}"/bin/init.sh'
    echo "Waiting for containers to start listening..."
    for i in `seq 1 60`; do
      if (cli "timeout 1 bash -c 'cat < /dev/null > /dev/tcp/ckan/5000'"); then
        echo "CKAN became ready on attempt $i"
        break
      else
        echo "CKAN not yet ready, retrying (attempt $i)..."
        sleep 1
      fi
    done
    if docker compose logs | grep -q "\[Error\]"; then exit 1; fi
    if docker compose logs | grep -q "Exception"; then exit 1; fi
    docker ps -a --filter name=^/${COMPOSE_PROJECT_NAME}_
    export DOCTOR_CHECK_CLI=0
}

down () {
    # Stop Docker containers and remove container, images, volumes and networks.
    title 'Stopping and removing old containers, images, volumes, networks'
    if [ -f "docker-compose.yml" ]; then docker compose down --volumes; fi
}

start () {
    # Start existing Docker containers.
    docker compose start "$@"
}

stop () {
    # Stop running Docker containers.
    docker compose stop "$@"
}

restart () {
    # Restart all stopped and running Docker containers.
    docker compose restart "$@"
}

logs () {
    # Show Docker logs.
    title "Output logs"
    # Loop through each container and wrap with github log groups
    services=$(docker compose ps --services)
    for service in $services; do
      echo "::group::$service"
      docker compose logs "$service"
      echo "::endgroup::"
    done
}

pull () {
    # Pull latest docker images.
    if [ ! -z "$(docker image ls -q)" ]; then docker image ls --format \"{{.Repository}}:{{.Tag}}\" | grep ckan/ckan- | grep -v none | xargs -n1 docker pull | cat; fi
}

cli () {
    # Start a shell inside CLI container or run a command.
    CKAN_CONTAINER=$(docker compose ps -q ckan)
    if [ "${#}" -ne 0 \]; then
      docker exec $CKAN_CONTAINER sh -c '. "${APP_DIR}"/bin/activate; cd $APP_DIR;'" $*"
    else
      docker exec $CKAN_CONTAINER sh -c '. "${APP_DIR}"/bin/activate && cd $APP_DIR && sh'
    fi
}

doctor () {
    # Find problems with current project setup.
    $BASEDIR/bin/doctor.sh "$@"
}

create_test_data () {
    # Install test site data.
    title "Installing a fresh site"
    cli '"${APP_DIR}"/bin/init.sh && "${APP_DIR}"/bin/create-test-data.sh'
}

clean () {
    # Remove containers and all build files.
    title "Cleaning up old builds"
    down
    # Remove other directories.
    # @todo: Add destinations below.
    rm -rf ./ckan
}

reset () {
    # "Reset environment: remove containers, all build, manually created and Drupal-Dev files."
    clean
    git ls-files --others -i --exclude-from=.git/info/exclude | xargs chmod 777
    git ls-files --others -i --exclude-from=.git/info/exclude | xargs rm -Rf
    find . -type d -not -path "./.git/*" -empty -delete
}

flush_redis () {
    # Flush Redis cache.
    docker exec -i $(docker compose ps -q redis) redis-cli flushall > /dev/null
}

lint () {
    # Lint code.
    title 'Check for lint'
    cli "flake8 ${@:-ckanext}" || \
    [ "${ALLOW_LINT_FAIL:-0}" -eq 1 ]
}

copy_local_files () {
    # Update files from local repo.
    docker cp . $(docker compose ps -q ckan):/srv/app/
    docker cp bin/ckan_cli $(docker compose ps -q ckan):/usr/bin/
    cli 'chmod -v u+x /usr/bin/ckan_cli "${APP_DIR}"/bin/*; cp -v .docker/test.ini $CKAN_INI'
}

test_unit () {
    # Run unit tests.
    title 'Run unit tests'
    cli 'pytest --ckan-ini=${CKAN_INI} --cov=ckanext "${APP_DIR}"/ckanext --junit-xml=test/junit/results.xml' || \
    [ "${ALLOW_UNIT_FAIL:-0}" -eq 1 ]
}

test_bdd () {
    # Create sample data and run scenario tests.
    create_test_data
    run_bdd_tests
}

run_bdd_tests () {
    title 'Run scenario tests'
    cli "rm -f test/screenshots/*"
    start_ckan_job_worker
    start_mailmock
    sleep 5
    JUNIT_OUTPUT="--junit --junit-directory=test/junit/"
    if [ "$BEHAVE_TAG" = "" ]; then
      _single_bdd_test_run "--tags=smoke" && _single_bdd_test_run "--tags=-smoke"
    else
      # run tests with the specified tag
      _single_bdd_test_run "--tags=$BEHAVE_TAG"
    fi
    stop_mailmock
    stop_ckan_job_worker
}

_single_bdd_test_run () {
    # Perform a single Behave run using the specified tag argument
    if [ $# -ge 1 ]; then
        TAGS="$1"
        shift
    fi
    cli "behave $JUNIT_OUTPUT --no-skipped ${*:-test/features} $TAGS" || [ "${ALLOW_BDD_FAIL:-0}" -eq 1 ]
}

process_artifacts () {
    # Download test artifacts eg screenshots
    cli "mkdir -p test/screenshots test/junit"
    mkdir -p /tmp/artifacts/behave /tmp/artifacts/junit
    docker cp "$(docker compose ps -q ckan)":/srv/app/test/screenshots /tmp/artifacts/behave/
    docker cp "$(docker compose ps -q ckan)":/srv/app/test/junit /tmp/artifacts/
}

start_mailmock () {
    # Starts email mock server used for email BDD tests
    title 'Starting mailmock'
    cli 'mailmock -p 8025 -o "${APP_DIR}"/test/emails' & # for debugging mailmock email output remove --no-stdout
}

stop_mailmock () {
    # Stops email mock server used for email BDD tests
    title 'Stopping mailmock'
    cli "killall -2 mailmock"
}

start_ckan_job_worker () {
    # Starts default CKAN background job worker
    title 'Starting default CKAN background job worker'
    cli "ckan_cli jobs clear && ckan_cli jobs worker &"
}

stop_ckan_job_worker () {
    # Stops CKAN background job worker
    title 'Stopping CKAN background job worker'
    # ignore failures from pkill killing itself
    cli 'pkill -f "jobs worker"' || true
}

# Utilities.
title () {
    printf "$(tput -Txterm setaf 4)==> ${1}$(tput -Txterm sgr0)\n"
}

line () {
    printf "$(tput -Txterm setaf 2)${1}$(tput -Txterm sgr0)${2}\n"
}

pre_flight () {
    doctor
}

if [ $# -lt 1 ]; then
    build
elif [ "$1" = "help" ] || [ "$1" = "--help" ]; then
    line "Available commands:"
    echo "build"
    echo "clean"
    echo "configure_docker"
    echo "create_test_data"
    echo "down"
    echo "info"
    echo "lint"
    echo "logs"
    echo "restart"
    echo "start"
    echo "stop"
    echo "test_bdd"
    echo "test_unit"
    echo "up"
else
    $@
fi
