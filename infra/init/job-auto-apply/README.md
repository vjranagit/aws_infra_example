# Job Auto Apply

This project uses [Playwright](https://playwright.dev/python/) to automate job applications on sites like LinkedIn.
It loads profile information from a `.env` file, fills common form fields, uploads your résumé and cover letter,
and optionally uses an LLM endpoint to generate a tailored cover letter.

## Setup

Copy `.env.example` to `.env` and edit it with your personal details and file paths.

## Run with Docker (recommended)

```bash
./run-docker.sh "https://www.linkedin.com/jobs/"    # pulls official Playwright image
```

## Manual setup

If you prefer running directly on the host:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install
python job_apply.py "https://www.linkedin.com/jobs/" linkedin
```

The script pauses for approval before submitting. Adjust selectors in `form_selectors.yml` as needed
for different job boards.
