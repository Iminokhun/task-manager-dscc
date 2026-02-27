#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/cloud}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
OVERRIDE_FILE="${OVERRIDE_FILE:-docker-compose.deploy.override.yml}"
WEB_IMAGE="${WEB_IMAGE:?WEB_IMAGE is required}"
WEB_TAG="${WEB_TAG:-latest}"

if [[ ! -d "$APP_DIR" ]]; then
  echo "APP_DIR does not exist: $APP_DIR"
  exit 1
fi

cd "$APP_DIR"

if [[ -d .git ]]; then
  git fetch origin "$DEPLOY_BRANCH"
  git checkout "$DEPLOY_BRANCH"
  git pull --ff-only origin "$DEPLOY_BRANCH"
fi

if [[ -n "${DOCKERHUB_USERNAME:-}" && -n "${DOCKERHUB_TOKEN:-}" ]]; then
  echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
fi

cat > "$OVERRIDE_FILE" <<EOF
services:
  web:
    image: ${WEB_IMAGE}:${WEB_TAG}
    build: null
EOF

docker compose -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" pull web
docker compose -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" run --rm web python manage.py migrate --noinput
docker compose -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" run --rm web python manage.py collectstatic --noinput
docker compose -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" up -d --no-deps web
docker compose -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" up -d nginx db redis
docker image prune -f

echo "Deployment complete: ${WEB_IMAGE}:${WEB_TAG}"
