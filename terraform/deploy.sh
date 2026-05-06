#!/bin/bash
# ─────────────────────────────────────────────
# Replydesk AI — Build, Push, and Deploy to EC2
# ─────────────────────────────────────────────

set -e

AWS_REGION="${AWS_REGION:-ap-southeast-1}"
APP_NAME="${APP_NAME:-replydesk-ai}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}"

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin \
  "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "🏗️  Building Docker image for linux/arm64 (t4g instances)..."
docker buildx create --use --name replydesk-builder 2>/dev/null || true
docker buildx build --platform linux/arm64 -t "$APP_NAME" --load -f ../Dockerfile ..

echo "🏷️  Tagging image..."
docker tag "$APP_NAME:latest" "$ECR_REPO:latest"

echo "📤 Pushing to ECR..."
docker push "$ECR_REPO:latest"

echo ""
echo "✅ Image pushed. Triggering EC2 update via SSM..."

# Get instance ID from tag
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:App,Values=$APP_NAME" "Name=instance-state-name,Values=running" \
  --query "Reservations[0].Instances[0].InstanceId" \
  --output text --region "$AWS_REGION")

if [ -z "$INSTANCE_ID" ] || [ "$INSTANCE_ID" = "None" ]; then
  echo "⚠️  No running EC2 instance found with App=$APP_NAME tag."
  echo "   Push complete — instance will pull the new image on next scheduled update (3am)."
  echo "   Or SSH in and run: /opt/replydesk/update.sh"
  exit 0
fi

echo "📡 Sending update command to instance $INSTANCE_ID..."
COMMAND_ID=$(aws ssm send-command \
  --instance-ids "$INSTANCE_ID" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["/opt/replydesk/update.sh"]' \
  --region "$AWS_REGION" \
  --query "Command.CommandId" \
  --output text)

echo "⏳ Waiting for deployment to complete (Command ID: $COMMAND_ID)..."
aws ssm wait command-executed \
  --command-id "$COMMAND_ID" \
  --instance-id "$INSTANCE_ID" \
  --region "$AWS_REGION"

STATUS=$(aws ssm get-command-invocation \
  --command-id "$COMMAND_ID" \
  --instance-id "$INSTANCE_ID" \
  --region "$AWS_REGION" \
  --query "Status" --output text)

if [ "$STATUS" = "Success" ]; then
  echo "✅ Deployment complete!"
  echo "   App URL: $(cd .. && terraform -chdir=terraform output -raw app_url 2>/dev/null || echo 'run: terraform output app_url')"
else
  echo "❌ Deployment failed with status: $STATUS"
  echo "   Check SSM command output in AWS Console or SSH into the instance."
  exit 1
fi
