#! /usr/bin/env sh

# Exit in case of error
set -e

export $(cat .env.production | sed 's/#.*//g' | xargs)

TAG=prod bash ./scripts/build.sh

TAG=prod \
bash ./scripts/deploy.sh
