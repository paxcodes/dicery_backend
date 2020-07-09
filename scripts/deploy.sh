#! /usr/bin/env sh

# Exit in case of error
set -e

DOMAIN=${DOMAIN?DOMAIN variable not set} \
TRAEFIK_TAG=${TRAEFIK_TAG?TRAEFIK_TAG variable not set} \
STACK_NAME=${STACK_NAME?STACK_NAME variable not set} \
TAG=${TAG?TAG variable not set} \
docker-compose \
-f docker-compose.yml \
config > docker-stack.yml

docker-auto-labels docker-stack.yml

docker stack deploy -c docker-stack.yml --with-registry-auth "${STACK_NAME?STACK_NAME variable not set}"
