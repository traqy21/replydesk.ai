# Replydesk AI — AWS Deployment (Terraform)

Deploys the app to a single **EC2 t4g.micro** instance — the cheapest viable AWS setup.
The instance runs Docker + nginx as a reverse proxy with free SSL via Let's Encrypt.

## Architecture

```
┌─────────────┐     ┌─────────────────────────────┐     ┌─────────────────┐
│   Client    │────▶│  EC2 t4g.micro              │────▶│  OpenAI API     │
│             │     │  nginx (SSL) → Docker        │     └─────────────────┘
└─────────────┘     └──────────────┬──────────────┘
                                   │
          ┌────────────────────────┼────────────────────┐
          │                        │                    │
   ┌──────▼──────┐  ┌──────────────▼──────┐  ┌─────────▼────────┐
   │  DynamoDB   │  │  Secrets Manager    │  │   CloudWatch     │
   │  users +    │  │  (3 secrets)        │  │   Logs + Alarms  │
   │  feedback   │  └─────────────────────┘  └──────────────────┘
   └─────────────┘
          │
   ┌──────▼──────┐
   │  AWS SES    │
   │  (email)    │
   └─────────────┘
```

## Cost Breakdown

| Resource | Est. Cost | Notes |
|----------|-----------|-------|
| EC2 t4g.micro | ~$6.11/month | 2 vCPU, 1 GB RAM, ARM (Graviton2) |
| Elastic IP | ~$0 | Free while attached to running instance |
| EBS gp3 20 GB | ~$1.60/month | Root volume |
| Secrets Manager (×3) | $1.20/month | 3 × $0.40/month |
| DynamoDB (×2) | ~$0 | Pay-per-request, free tier covers low traffic |
| ECR | ~$0 | First 500 MB/month free |
| SES | ~$0 | First 62,000 emails/month free |
| CloudWatch Logs | ~$0.50/month | ~5 GB ingestion at low traffic |
| CloudWatch Alarms (×2) | $0.20/month | 2 × $0.10/month |
| **Total** | **~$10/month** | |

> **~$10/month** vs ~$27/month for ECS Express Mode — saving ~$17/month by dropping the ALB.
> Trade-off: you manage the instance (OS updates, Docker restarts) instead of AWS doing it.

---

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.5.0
- Docker installed locally (for building the image)
- A domain name with DNS access (for SSL via Let's Encrypt)
- An SSH key pair (`ssh-keygen -t rsa -b 4096` if you don't have one)

---

## Setup

### 1. Configure variables

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
aws_region       = "us-east-1"
app_name         = "replydesk-ai"
openai_api_key   = "sk-..."
instance_type    = "t4g.micro"
ssh_public_key   = "ssh-rsa AAAA..."   # cat ~/.ssh/id_rsa.pub
ssh_allowed_cidr = "YOUR_IP/32"        # curl ifconfig.me to find your IP
domain           = "app.yourdomain.com"
ses_sender_email = "noreply@yourdomain.com"
admin_email      = "admin@yourdomain.com"
admin_password   = "a-strong-password"
github_repo      = "your-username/replydesk-ai"
app_url          = "https://app.yourdomain.com"
```

### 2. (Recommended) Enable remote state

Uncomment the `backend "s3"` block in `main.tf` before first apply to prevent state corruption.

### 3. Create ECR and push image first

The EC2 instance pulls the image on boot — it must exist in ECR before the instance launches.

```bash
terraform init
terraform apply -target=aws_ecr_repository.app

chmod +x deploy.sh
./deploy.sh   # builds and pushes the Docker image
```

### 4. Deploy infrastructure

```bash
terraform apply
```

This creates the EC2 instance, Elastic IP, security group, DynamoDB tables, Secrets Manager secrets, SES identity, and CloudWatch resources.

### 5. Point your domain to the Elastic IP

```bash
terraform output elastic_ip
```

Create an **A record** in your DNS provider pointing your domain to this IP.
SSL will be provisioned automatically by Let's Encrypt once DNS propagates (~5 minutes).

### 6. Verify SES sender email

AWS sends a verification email to `ses_sender_email`. Click the link before password reset emails will work.

> ⚠️ SES starts in **sandbox mode** — request production access in the AWS console before going live.

### 7. Update app_url

After DNS is set up, update `app_url` in `terraform.tfvars` and run `terraform apply` again so password reset emails contain the correct link.

---

## Environment Variables

Pulled from Secrets Manager and written to `/opt/replydesk/.env` on the instance at boot:

| Variable | Source | Description |
|----------|--------|-------------|
| `OPENAI_API_KEY` | Secrets Manager | OpenAI API key |
| `ADMIN_EMAIL` | Secrets Manager | Default admin account email |
| `ADMIN_PASSWORD` | Secrets Manager | Default admin account password |
| `DYNAMODB_TABLE` | Env var | Users DynamoDB table name |
| `AWS_REGION` | Env var | AWS region |
| `SES_SENDER_EMAIL` | Env var | From address for reset emails |
| `APP_URL` | Env var | Public app URL (used in reset email links) |
| `APP_NAME` | Env var | App name (used to derive feedback table name) |
| `LOG_LEVEL` | Env var | Logging level (`INFO` by default) |

---

## Storage Backend

- **Local development** — uses `users.json` and `feedback.json`
- **Production (AWS)** — uses DynamoDB when `DYNAMODB_TABLE` is set

---

## Outputs

| Output | Description |
|--------|-------------|
| `elastic_ip` | Public IP — point your domain A record here |
| `app_url` | Live application URL |
| `ecr_repository_url` | ECR URL for pushing Docker images |
| `dynamodb_table_name` | Users DynamoDB table name |
| `dynamodb_feedback_table_name` | Feedback DynamoDB table name |
| `ses_sender_email` | Verified SES sender address |
| `cloudwatch_log_group` | CloudWatch log group name |
| `github_actions_role_arn` | IAM role ARN for GitHub Actions |
| `ssh_command` | Ready-to-use SSH command |

---

## Deploying Updates

Push a new image and trigger a rolling update via SSM (no SSH needed):

```bash
./deploy.sh
```

The script:
1. Builds and pushes the Docker image to ECR
2. Sends an SSM command to the EC2 instance to pull and restart the container
3. Waits for confirmation and reports success/failure

The instance also auto-updates daily at 3am via a cron job.

---

## SSH Access

```bash
terraform output ssh_command
# ssh -i ~/.ssh/your-key ec2-user@<elastic-ip>
```

Useful commands on the instance:

```bash
# View app logs
docker logs replydesk -f

# Manually trigger update
/opt/replydesk/update.sh

# Restart app
docker restart replydesk

# Check nginx status
systemctl status nginx
```

---

## Logging & Monitoring

Application logs go to CloudWatch at `/replydesk-ai/app` via the CloudWatch agent.

Two metric alarms:

| Alarm | Trigger |
|-------|---------|
| `replydesk-ai-error-rate` | 5+ errors in 5 minutes |
| `replydesk-ai-account-lockouts` | 3+ lockouts in 5 minutes |

---

## CI/CD (GitHub Actions)

- **`ci.yml`** — lints and validates on every push/PR
- **`deploy.yml`** — builds, scans, pushes to ECR, triggers EC2 update via SSM on push to `main`

Uses **OIDC** — no AWS keys stored in GitHub.

### Setup

1. Run `terraform apply`
2. `terraform output github_actions_role_arn` — copy the ARN
3. Add to GitHub repository secrets:

| Secret | Value |
|--------|-------|
| `AWS_DEPLOY_ROLE_ARN` | ARN from step 2 |
| `AWS_REGION` | e.g. `us-east-1` |
| `APP_NAME` | e.g. `replydesk-ai` |

---

## Security Notes

- SSH restricted to `ssh_allowed_cidr` — set this to your IP only
- All secrets in Secrets Manager — never in plaintext Terraform state
- EC2 instance has an IAM role with least-privilege permissions
- EBS root volume is encrypted
- DynamoDB tables have point-in-time recovery enabled
- ECR image scanning enabled on push
- App container runs as non-root user (set in Dockerfile)

---

## Tear Down

```bash
terraform destroy
```

> `force_delete = true` on the ECR repository means it will be deleted even if it contains images.
