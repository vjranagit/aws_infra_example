# Install Docker and start service
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl enable --now docker

# Run the job auto-apply script inside the official Playwright container
cd /home/ubuntu/job-auto-apply
cp .env.example .env

PLAYWRIGHT_IMAGE=${PLAYWRIGHT_IMAGE:-mcr.microsoft.com/playwright/python:v1.47.0}
CONTAINER_NAME=${CONTAINER_NAME:-job-auto-apply}
PWDEBUG_PORT=${PWDEBUG_PORT:-9333}
sudo docker pull "$PLAYWRIGHT_IMAGE"

JOB_URL=${JOB_URL:-"https://www.linkedin.com/jobs/"}
echo "[boot-strap] starting container $CONTAINER_NAME with Playwright inspector on port $PWDEBUG_PORT"
sudo docker run --rm --shm-size=1gb \
  --name "$CONTAINER_NAME" \
  --env-file .env \
  -e PWDEBUG=1 \
  -e HEADLESS=false \
  -e JOB_URL="$JOB_URL" \
  -p "$PWDEBUG_PORT:9333" \
  -v "$(pwd)":/app \
  "$PLAYWRIGHT_IMAGE" \
  bash -lc "pip install -r /app/requirements.txt && python /app/job_apply.py \"$JOB_URL\" linkedin" || true

