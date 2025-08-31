# Install Docker and start service
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl enable --now docker

# Run the job auto-apply script inside the official Playwright container
cd /home/ubuntu/job-auto-apply
cp .env.example .env

PLAYWRIGHT_IMAGE=${PLAYWRIGHT_IMAGE:-mcr.microsoft.com/playwright/python:v1.47.0}
sudo docker pull "$PLAYWRIGHT_IMAGE"

JOB_URL=${JOB_URL:-"https://www.linkedin.com/jobs/"}
sudo docker run --rm --shm-size=1gb \
  --env-file .env \
  -e JOB_URL="$JOB_URL" \
  -v "$(pwd)":/app \
  "$PLAYWRIGHT_IMAGE" \
  bash -lc "pip install -r /app/requirements.txt && python /app/job_apply.py \"$JOB_URL\" linkedin" || true

