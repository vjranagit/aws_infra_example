#!/usr/bin/env bash
set -euo pipefail

JOB_URL=${1:-"https://www.linkedin.com/jobs/"}
PLAYWRIGHT_IMAGE=${PLAYWRIGHT_IMAGE:-mcr.microsoft.com/playwright/python:v1.47.0}

docker pull "$PLAYWRIGHT_IMAGE"

docker run --rm --shm-size=1gb \
  --env-file .env \
  -e JOB_URL="$JOB_URL" \
  -v "$(pwd)":/app \
  "$PLAYWRIGHT_IMAGE" \
  bash -lc "pip install -r /app/requirements.txt && python /app/job_apply.py \"$JOB_URL\" linkedin"
