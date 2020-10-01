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


DOMAIN=${DOMAIN?DOMAIN variable not set} \
TRAEFIK_TAG=${TRAEFIK_TAG?TRAEFIK_TAG variable not set} \
STACK_NAME=${STACK_NAME?STACK_NAME variable not set} \
TAG=${TAG?TAG variable not set} \
docker-compose \
-f "${DOCKER_COMPOSE_FILE}" \
config > docker-stack.yml

docker-auto-labels docker-stack.yml

docker stack deploy -c docker-stack.yml --with-registry-auth "${STACK_NAME?STACK_NAME variable not set}"
