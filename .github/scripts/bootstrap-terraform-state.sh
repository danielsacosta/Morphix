#!/usr/bin/env bash
set -euo pipefail

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
STATE_BUCKET="${TG_STATE_BUCKET:-${PROJECT_NAME}-${ENVIRONMENT}-terraform-state-${ACCOUNT_ID}}"
LOCK_TABLE="${TG_LOCK_TABLE:-${PROJECT_NAME}-${ENVIRONMENT}-terraform-locks}"

if [[ -n "${GITHUB_ENV:-}" ]]; then
  echo "TG_STATE_BUCKET=${STATE_BUCKET}" >> "$GITHUB_ENV"
  echo "TG_LOCK_TABLE=${LOCK_TABLE}" >> "$GITHUB_ENV"
fi

if aws s3api head-bucket --bucket "${STATE_BUCKET}" 2>/dev/null; then
  echo "Terraform state bucket already exists: ${STATE_BUCKET}"
else
  echo "Creating Terraform state bucket: ${STATE_BUCKET}"
  if [[ "${AWS_REGION}" == "us-east-1" ]]; then
    aws s3api create-bucket --bucket "${STATE_BUCKET}" --region "${AWS_REGION}"
  else
    aws s3api create-bucket \
      --bucket "${STATE_BUCKET}" \
      --region "${AWS_REGION}" \
      --create-bucket-configuration LocationConstraint="${AWS_REGION}"
  fi
fi

aws s3api put-bucket-versioning \
  --bucket "${STATE_BUCKET}" \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket "${STATE_BUCKET}" \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

aws s3api put-public-access-block \
  --bucket "${STATE_BUCKET}" \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

if aws dynamodb describe-table --table-name "${LOCK_TABLE}" >/dev/null 2>&1; then
  echo "Terraform lock table already exists: ${LOCK_TABLE}"
else
  echo "Creating Terraform lock table: ${LOCK_TABLE}"
  aws dynamodb create-table \
    --table-name "${LOCK_TABLE}" \
    --billing-mode PAY_PER_REQUEST \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH
  aws dynamodb wait table-exists --table-name "${LOCK_TABLE}"
fi
