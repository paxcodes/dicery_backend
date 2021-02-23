# Configuration
export BASE_DOMAIN=api.dicery.margret.pw
export BASE_NAME=api-dicery-margret-pw
export ENV_NAME_SHORT=stag
export ENV_NAME_LONG=staging
export TAG=$ENV_NAME_SHORT
export DOMAIN=$ENV_NAME_SHORT.$BASE_DOMAIN
bash scripts/build.sh
export TRAEFIK_TAG=$ENV_NAME_SHORT.$BASE_DOMAIN
export STACK_NAME=$ENV_NAME_SHORT-$BASE_NAME
bash scripts/deploy.sh
docker service update --force $ENV_NAME_SHORT-${BASE_NAME}_backend -d
