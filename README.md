# Replydesk AI

A Streamlit web app for generating client replies, emails, task summaries, and daily reports using OpenAI (GPT-4o-mini).

## Requirements

- Python 3.12+
- Docker & Docker Compose (optional, recommended for containerized deployment)
- OpenAI API key

## Setup

1. Copy or create a `.env` file in the project root:

```bash
cp .env.example .env
```

2. Fill in your values:

```env
OPENAI_API_KEY=your_openai_api_key_here
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=a-strong-password
```

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run main.py
```

Then open the URL shown in the terminal, usually `http://localhost:8501`.

## Run with Docker

Build and start the app using Docker Compose:

```bash
docker-compose up --build
```

The app will be available at `http://localhost:8501`.

## Project Structure

```
.
├── main.py                  # Entry point — routing, sidebar, auth gate
├── config.py                # Environment loading, OpenAI client, constants
├── auth.py                  # Login, registration, session, rate limiting, brute-force protection
├── profile.py               # Profile/settings page logic
├── prompts.py               # Prompt templates for each tool
├── ui.py                    # Reusable UI components
├── theme.py                 # Dark/light theme and responsive CSS
├── logger.py                # Structured JSON logging + CloudWatch via watchtower
├── feedback_store.py        # Feedback persistence (JSON locally, DynamoDB in prod)
├── pages/
│   ├── tools.py             # Main generation interface
│   ├── history.py           # Past generations log
│   ├── settings.py          # Profile settings
│   ├── feedback.py          # Feedback form
│   ├── admin.py             # Admin panel (users, stats, feedback, system)
│   ├── landing.py           # Public landing page
│   ├── privacy_policy.py    # Privacy policy
│   └── reset_password.py    # Password reset flow
├── requirements.txt         # Python dependencies
├── Dockerfile               # Python 3.12-slim, non-root user, healthcheck
├── docker-compose.yml       # Single-service compose config with resource limits
├── .env.example             # Template for required environment variables
├── ruff.toml                # Linter configuration
├── .github/workflows/       # CI/CD pipelines (lint + deploy)
├── terraform/               # AWS infrastructure (EC2 + Docker)
└── documentations/          # Project docs and checklists
```

## Features

- **4 AI tools** — Client Reply, Email Generator, Task Summary, Daily Report
- **Tone selection** — Friendly, Formal, Professional, Casual
- **Dynamic prompts** — AI responses tailored to your job role
- **Generation history** — Review, reload, and filter past outputs
- **Inline editing** — Edit generated output before copying
- **User authentication** — Email + password with bcrypt hashing
- **Session timeout** — Auto-logout after 30 minutes of inactivity
- **Rate limiting** — 50 generations/day per user
- **Brute-force protection** — Account lockout after 5 failed login attempts
- **Password reset** — Email-based via AWS SES
- **Admin panel** — User management, usage stats, feedback view
- **Landing page** — Public-facing page for new visitors
- **Privacy policy** — GDPR-ready privacy policy page
- **Dark/light theme** — Toggle between themes in the sidebar
- **Responsive layout** — Optimized for desktop and mobile
- **CloudWatch logging** — Structured JSON logs with metric alarms

## Deploy to AWS

The project includes Terraform configuration for deploying to a single **EC2 t4g.micro** instance — the cheapest viable AWS setup (~$10/month). The instance runs Docker + nginx as a reverse proxy with free SSL via Let's Encrypt.

### Architecture

```
┌─────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   Client    │────▶│  EC2 t4g.micro       │────▶│  OpenAI API     │
│             │     │  nginx + Docker       │     └─────────────────┘
└─────────────┘     └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
   ┌──────▼──────┐  ┌──────────▼──────┐  ┌─────────▼────────┐
   │  DynamoDB   │  │  Secrets        │  │   CloudWatch     │
   │  users +    │  │  Manager        │  │   Logs + Alarms  │
   │  feedback   │  │  (3 secrets)    │  └──────────────────┘
   └─────────────┘  └─────────────────┘
                               │
                        ┌──────▼──────┐
                        │  AWS SES    │
                        │  (email)    │
                        └─────────────┘
```

### AWS Resources & Costs

| Resource | Purpose | Est. Cost |
|----------|---------|-----------|
| EC2 t4g.micro | Runs the container (2 vCPU, 1 GB RAM) | ~$6.11/month |
| Elastic IP | Stable public IP address | ~$0 |
| EBS gp3 20 GB | Root volume (encrypted) | ~$1.60/month |
| Secrets Manager (×3) | OpenAI key, admin email, admin password | $1.20/month |
| DynamoDB (×2) | User + feedback storage, pay-per-request | ~$0 |
| ECR | Docker image storage | ~$0 (free tier) |
| SES | Password reset emails | ~$0 (62k free/month) |
| CloudWatch Logs | Application logs, 30-day retention | ~$0.50/month |
| CloudWatch Alarms (×2) | Error rate + lockout alerts | $0.20/month |
| IAM Roles | Least-privilege permissions | Free |

**Estimated total: ~$10/month** for light usage.

### Deployment Steps

See `terraform/README.md` for full instructions. Quick summary:

1. Configure variables:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

2. Create ECR and push image first:

```bash
terraform init
terraform apply -target=aws_ecr_repository.app
chmod +x deploy.sh && ./deploy.sh
```

3. Deploy the rest:

```bash
terraform apply
```

4. Get your app URL:

```bash
terraform output app_url
```

### Storage Backend

The app automatically detects the environment:
- **Local development** — uses `users.json` and `feedback.json`
- **AWS (production)** — uses DynamoDB when `DYNAMODB_TABLE` env var is set

No code changes needed between environments.

### CI/CD

GitHub Actions workflows are included in `.github/workflows/`:
- **`ci.yml`** — lints and validates on every push/PR
- **`deploy.yml`** — builds, scans, pushes to ECR, and triggers EC2 update via SSM on push to `main` using OIDC (no stored AWS keys)

See `terraform/README.md` for GitHub Actions setup steps.

### Tear Down

```bash
cd terraform
terraform destroy
```

## Notes

- Make sure `OPENAI_API_KEY` is set before starting the application.
- If you use Docker, the `.env` file is loaded automatically by `docker-compose.yml`.
- The default admin account is seeded from `ADMIN_EMAIL` and `ADMIN_PASSWORD` env vars on first startup.
- SES starts in sandbox mode — request production access in the AWS console before going live.
