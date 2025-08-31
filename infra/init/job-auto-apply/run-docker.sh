#!/usr/bin/env bash
set -euo pipefail

JOB_URL=${1:-"https://www.linkedin.com/jobs/"}
PLAYWRIGHT_IMAGE=${PLAYWRIGHT_IMAGE:-mcr.microsoft.com/playwright/python:v1.47.0}
CONTAINER_NAME=${CONTAINER_NAME:-job-auto-apply}
PWDEBUG_PORT=${PWDEBUG_PORT:-9333}

docker pull "$PLAYWRIGHT_IMAGE"

echo "[run-docker] starting container $CONTAINER_NAME with Playwright inspector on port $PWDEBUG_PORT"

docker run --rm --shm-size=1gb \
  --name "$CONTAINER_NAME" \
  --env-file .env \
  -e PWDEBUG=1 \
  -e HEADLESS=false \
  -e JOB_URL="$JOB_URL" \
  -p "$PWDEBUG_PORT:9333" \
  -v "$(pwd)":/app \
  "$PLAYWRIGHT_IMAGE" \
  bash -lc "pip install -r /app/requirements.txt && python /app/job_apply.py \"$JOB_URL\" linkedin"
