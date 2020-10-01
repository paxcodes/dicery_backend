#! /usr/bin/env sh

# Exit in case of error
set -e

# If DICERY_ENV is empty
if [ -z "$DICERY_ENV" ]
then
    export DOCKER_COMPOSE_FILE=docker-compose.yml
else
    export DOCKER_COMPOSE_FILE=docker-compose."${DICERY_ENV}".yml
fi

TAG=${TAG?TAG variable not set} \
docker-compose \
-f "${DOCKER_COMPOSE_FILE}" \
build
