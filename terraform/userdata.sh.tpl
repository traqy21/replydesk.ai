#!/bin/bash
set -e

# ─────────────────────────────────────────────
# Replydesk AI — EC2 Bootstrap Script
# Runs once on first launch via user_data
# ─────────────────────────────────────────────

# System update and dependencies
dnf update -y
dnf install -y docker nginx certbot python3-certbot-nginx aws-cli jq

# Start and enable Docker
systemctl enable --now docker
usermod -aG docker ec2-user

# SSM agent (enables remote deploy via deploy.sh without SSH)
dnf install -y amazon-ssm-agent
systemctl enable --now amazon-ssm-agent

# ── Pull secrets from Secrets Manager ────────
OPENAI_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id "${app_name}/openai-api-key" \
  --region "${aws_region}" \
  --query SecretString --output text)

ADMIN_EMAIL=$(aws secretsmanager get-secret-value \
  --secret-id "${app_name}/admin-email" \
  --region "${aws_region}" \
  --query SecretString --output text)

ADMIN_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id "${app_name}/admin-password" \
  --region "${aws_region}" \
  --query SecretString --output text)

# ── Write .env file ───────────────────────────
mkdir -p /opt/replydesk

cat > /opt/replydesk/.env <<EOF
OPENAI_API_KEY=$OPENAI_API_KEY
ADMIN_EMAIL=$ADMIN_EMAIL
ADMIN_PASSWORD=$ADMIN_PASSWORD
DYNAMODB_TABLE=${dynamodb_table}
AWS_REGION=${aws_region}
SES_SENDER_EMAIL=${ses_sender_email}
APP_NAME=${app_name}
APP_URL=https://${domain}
LOG_LEVEL=INFO
EOF

# ── Pull and run the app container ───────────
aws ecr get-login-password --region "${aws_region}" | \
  docker login --username AWS --password-stdin "${ecr_repo}"

docker pull "${ecr_repo}:latest"

docker run -d \
  --name replydesk \
  --restart unless-stopped \
  --env-file /opt/replydesk/.env \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e ADMIN_EMAIL="$ADMIN_EMAIL" \
  -e ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  -e SES_SENDER_EMAIL="${ses_sender_email}" \
  -p 8501:8501 \
  "${ecr_repo}:latest"

# ── Configure nginx as reverse proxy ─────────
mkdir -p /opt/replydesk/static

# OG social share page
cat > /opt/replydesk/static/index.html <<'OGHTML'
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Replydesk AI — Free AI Writing Tools for Professionals</title>
  <meta name="description" content="Generate client replies, emails, meeting notes, daily reports and more in seconds. Free to try — 10 generations per day." />
  <meta property="og:title" content="Replydesk AI — Free AI Writing Tools for Professionals" />
  <meta property="og:description" content="Generate client replies, emails, meeting notes, daily reports and more in seconds. Free to try — 10 generations per day, no credit card required." />
  <meta property="og:image" content="https://replydesk-ai.com/og-image.png" />
  <meta property="og:url" content="https://replydesk-ai.com" />
  <meta property="og:type" content="website" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Replydesk AI — Free AI Writing Tools for Professionals" />
  <meta name="twitter:description" content="Generate client replies, emails, meeting notes, daily reports and more in seconds. Free to try." />
  <meta name="twitter:image" content="https://replydesk-ai.com/og-image.png" />
  <meta http-equiv="refresh" content="0; url=https://replydesk-ai.com/" />
</head>
<body><p>Loading <a href="https://replydesk-ai.com/">Replydesk AI</a>...</p></body>
</html>
OGHTML

cat > /etc/nginx/conf.d/replydesk.conf <<NGINX
server {
    listen 80;
    server_name ${domain};

    location / {
        proxy_pass         http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade \$http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host \$host;
        proxy_set_header   X-Real-IP \$remote_addr;
        proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}
NGINX

systemctl enable --now nginx

# ── Obtain SSL certificate via Let's Encrypt ──
# Only runs if a real domain is configured
if [ "${domain}" != "localhost" ] && [ -n "${domain}" ]; then
  certbot --nginx \
    --non-interactive \
    --agree-tos \
    --email "${ses_sender_email}" \
    --domains "${domain}" \
    --redirect

  # After certbot rewrites the config, add static routes for OG image and share page
  # Insert before the closing } of the SSL server block
  sed -i '/proxy_read_timeout 86400;/a\    }\n\n    location = \/share {\n        root \/opt\/replydesk\/static;\n        try_files \/index.html =404;\n    }\n\n    location = \/og-image.svg {\n        root \/opt\/replydesk\/static;\n        add_header Cache-Control "public, max-age=86400";\n    }\n\n    location \/ {' /etc/nginx/conf.d/replydesk.conf
  systemctl reload nginx
fi

# ── CloudWatch agent for log shipping ─────────
dnf install -y amazon-cloudwatch-agent

cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json <<CWAGENT
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/replydesk/*.log",
            "log_group_name": "${log_group}",
            "log_stream_name": "{instance_id}/app",
            "timezone": "UTC"
          }
        ]
      }
    }
  }
}
CWAGENT

/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
  -s

# ── Auto-update script (daily pull + restart) ─
cat > /opt/replydesk/update.sh <<'UPDATE'
#!/bin/bash
set -e
AWS_REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)
ECR_REPO="${ecr_repo}"

aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$ECR_REPO"

# Re-fetch secrets in case they changed
OPENAI_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id "replydesk-ai/openai-api-key" \
  --region "$AWS_REGION" \
  --query SecretString --output text)

ADMIN_EMAIL=$(aws secretsmanager get-secret-value \
  --secret-id "replydesk-ai/admin-email" \
  --region "$AWS_REGION" \
  --query SecretString --output text)

ADMIN_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id "replydesk-ai/admin-password" \
  --region "$AWS_REGION" \
  --query SecretString --output text)

docker pull "$ECR_REPO:latest"
docker stop replydesk || true
docker rm replydesk || true
docker run -d \
  --name replydesk \
  --restart unless-stopped \
  --env-file /opt/replydesk/.env \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e ADMIN_EMAIL="$ADMIN_EMAIL" \
  -e ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  -e SES_SENDER_EMAIL="noreply@replydesk-ai.com" \
  -p 8501:8501 \
  "$ECR_REPO:latest"
UPDATE

chmod +x /opt/replydesk/update.sh

# Run update daily at 3am
echo "0 3 * * * root /opt/replydesk/update.sh >> /var/log/replydesk-update.log 2>&1" \
  > /etc/cron.d/replydesk-update

echo "✅ Replydesk AI bootstrap complete."
