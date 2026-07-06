#!/bin/bash
set -uo pipefail

# Idempotent: re-running on a persisted LocalStack volume should be a no-op.
# We swallow "already exists" errors instead of failing the script.

echo ">> Morphix local init: provisioning LocalStack resources"

# ---------------------------------------------------------------------------
# DynamoDB: jobs table (mirrors infra/blueprints/modules/jobs-db/main.tf)
# ---------------------------------------------------------------------------
awslocal dynamodb create-table \
  --table-name morphix-dev-jobs \
  --attribute-definitions \
    AttributeName=job_id,AttributeType=S \
    AttributeName=user_id,AttributeType=S \
    AttributeName=created_at,AttributeType=S \
    AttributeName=status,AttributeType=S \
    AttributeName=updated_at,AttributeType=S \
  --key-schema AttributeName=job_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_IMAGE \
  --global-secondary-indexes '[
    {"IndexName":"GSI1","KeySchema":[{"AttributeName":"user_id","KeyType":"HASH"},{"AttributeName":"created_at","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}},
    {"IndexName":"GSI2","KeySchema":[{"AttributeName":"status","KeyType":"HASH"},{"AttributeName":"updated_at","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}
  ]' &>/dev/null

awslocal dynamodb update-time-to-live \
  --table-name morphix-dev-jobs \
  --time-to-live-specification AttributeName=expires_at,Enabled=true &>/dev/null

# ---------------------------------------------------------------------------
# DynamoDB: websocket connections table
# (mirrors aws_dynamodb_table.websocket_connections in infra/blueprints/modules/api/main.tf)
# ---------------------------------------------------------------------------
awslocal dynamodb create-table \
  --table-name morphix-dev-websocket-connections \
  --attribute-definitions \
    AttributeName=connection_id,AttributeType=S \
    AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=connection_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes '[
    {"IndexName":"user_id-index","KeySchema":[{"AttributeName":"user_id","KeyType":"HASH"}],"Projection":{"ProjectionType":"ALL"}}
  ]' &>/dev/null

awslocal dynamodb update-time-to-live \
  --table-name morphix-dev-websocket-connections \
  --time-to-live-specification AttributeName=expires_at,Enabled=true &>/dev/null

# ---------------------------------------------------------------------------
# S3 buckets with permissive CORS for browser uploads/downloads via presigned URLs
# ---------------------------------------------------------------------------
awslocal s3 mb s3://morphix-dev-input &>/dev/null
awslocal s3 mb s3://morphix-dev-output &>/dev/null

awslocal s3api put-bucket-cors --bucket morphix-dev-input --cors-configuration '{
  "CORSRules": [
    {
      "AllowedOrigins": ["http://localhost:5173", "http://127.0.0.1:5173"],
      "AllowedMethods": ["GET", "PUT", "HEAD"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"]
    }
  ]
}' &>/dev/null

awslocal s3api put-bucket-cors --bucket morphix-dev-output --cors-configuration '{
  "CORSRules": [
    {
      "AllowedOrigins": ["http://localhost:5173", "http://127.0.0.1:5173"],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedHeaders": ["*"]
    }
  ]
}' &>/dev/null

# ---------------------------------------------------------------------------
# SQS: conversion queue + DLQ with redrive policy
# ---------------------------------------------------------------------------
awslocal sqs create-queue --queue-name morphix-dev-conversions-dlq &>/dev/null

awslocal sqs create-queue \
  --queue-name morphix-dev-conversions \
  --attributes VisibilityTimeout=180 &>/dev/null

DLQ_URL=$(awslocal sqs get-queue-url --queue-name morphix-dev-conversions-dlq --query 'QueueUrl' --output text)
DLQ_ARN=$(awslocal sqs get-queue-attributes \
  --queue-url "$DLQ_URL" \
  --attribute-names QueueArn \
  --query 'Attributes.QueueArn' --output text)

awslocal sqs set-queue-attributes \
  --queue-url "$(awslocal sqs get-queue-url --queue-name morphix-dev-conversions --query 'QueueUrl' --output text)" \
  --attributes RedrivePolicy="{\"deadLetterTargetArn\":\"$DLQ_ARN\",\"maxReceiveCount\":\"3\"}" &>/dev/null

echo ">> Morphix local init: done"