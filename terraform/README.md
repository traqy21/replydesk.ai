# Replydesk AI — AWS Deployment (Terraform)

Deploys the app to **AWS App Runner** with ECR, Secrets Manager, and DynamoDB.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Client    │────▶│  App Runner  │────▶│  OpenAI API     │
└─────────────┘     └──────┬───────┘     └─────────────────┘
                           │
                    ┌──────┴───────┐
                    │              │
              ┌─────▼─────┐  ┌────▼────────────┐
              │ DynamoDB   │  │ Secrets Manager  │
              │ (users)    │  │ (API key)        │
              └────────────┘  └─────────────────┘
```

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.5.0
- Docker installed locally

## Setup

1. Copy the example variables file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

2. Edit `terraform.tfvars` with your values (especially `openai_api_key`).

3. Initialize and apply:

```bash
terraform init
terraform plan
terraform apply
```

4. Push your Docker image:

```bash
chmod +x deploy.sh
./deploy.sh
```

## Resources Created

| Resource | Purpose | Estimated Cost |
|----------|---------|----------------|
| ECR Repository | Docker image storage | ~$0 (free tier) |
| App Runner | Runs the container | ~$5–15/month |
| DynamoDB | User storage | ~$0 (pay-per-request) |
| Secrets Manager | Stores OpenAI API key | ~$0.40/month |
| IAM Roles | Permissions | Free |

**Estimated total: ~$5–16/month** for light usage.

## Outputs

After `terraform apply`, you'll get:

- `app_url` — Your live application URL
- `ecr_repository_url` — Where to push Docker images
- `dynamodb_table_name` — DynamoDB table for user data

## Tear Down

```bash
terraform destroy
```

## Notes

- App Runner auto-deploys when a new image is pushed to ECR.
- The app uses Streamlit's built-in health check endpoint (`/_stcore/health`).
- Scaling is set to 1–2 instances by default. Adjust in `terraform.tfvars`.
- You'll need to update `auth.py` to use DynamoDB instead of `users.json` for production. See the `config.py` `DYNAMODB_TABLE` env var that's injected at runtime.
