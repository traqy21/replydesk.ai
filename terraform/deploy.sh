#!/bin/bash
# ─────────────────────────────────────────────
# Replydesk AI — Build, Push, and Deploy
# ─────────────────────────────────────────────

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
APP_NAME="${APP_NAME:-replydesk-ai}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}"

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "🏗️  Building Docker image..."
docker build -t "$APP_NAME" ..

echo "🏷️  Tagging image..."
docker tag "$APP_NAME:latest" "$ECR_REPO:latest"

echo "📤 Pushing to ECR..."
docker push "$ECR_REPO:latest"

echo "✅ Done! App Runner will auto-deploy the new image."
echo "   URL: Check 'terraform output app_url' for your app URL."
