#!/usr/bin/env bash
set -euo pipefail

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
NAME_PREFIX="${PROJECT_NAME}-${ENVIRONMENT}"
STATE_BUCKET="${TG_STATE_BUCKET:-${PROJECT_NAME}-${ENVIRONMENT}-terraform-state-${ACCOUNT_ID}}"
LOCK_TABLE="${TG_LOCK_TABLE:-${PROJECT_NAME}-${ENVIRONMENT}-terraform-locks}"

empty_bucket() {
  local bucket="$1"

  if ! aws s3api head-bucket --bucket "${bucket}" >/dev/null 2>&1; then
    echo "Bucket ${bucket} does not exist. Skipping."
    return
  fi

  echo "Emptying s3://${bucket}"
  aws s3 rm "s3://${bucket}" --recursive || true

  while true; do
    local versions_file
    local chunk_dir
    versions_file="$(mktemp)"
    chunk_dir="$(mktemp -d)"

    aws s3api list-object-versions --bucket "${bucket}" > "${versions_file}"

    local object_count
    object_count="$(python3 - "${versions_file}" "${chunk_dir}" <<'PY'
import json
import pathlib
import sys

versions_file = pathlib.Path(sys.argv[1])
chunk_dir = pathlib.Path(sys.argv[2])
data = json.loads(versions_file.read_text())
objects = [
    {"Key": item["Key"], "VersionId": item["VersionId"]}
    for item in data.get("Versions", []) + data.get("DeleteMarkers", [])
]

for index in range(0, len(objects), 1000):
    payload = {"Objects": objects[index:index + 1000], "Quiet": True}
    (chunk_dir / f"delete-{index // 1000}.json").write_text(json.dumps(payload))

print(len(objects))
PY
)"

    if [[ "${object_count}" == "0" ]]; then
      rm -f "${versions_file}"
      rm -rf "${chunk_dir}"
      break
    fi

    for delete_file in "${chunk_dir}"/delete-*.json; do
      [[ -e "${delete_file}" ]] || continue
      aws s3api delete-objects --bucket "${bucket}" --delete "file://${delete_file}" >/dev/null
    done

    rm -f "${versions_file}"
    rm -rf "${chunk_dir}"
  done
}

delete_bucket() {
  local bucket="$1"

  if ! aws s3api head-bucket --bucket "${bucket}" >/dev/null 2>&1; then
    echo "Bucket ${bucket} does not exist. Skipping delete."
    return
  fi

  empty_bucket "${bucket}"
  echo "Deleting bucket ${bucket}"
  aws s3api delete-bucket --bucket "${bucket}"
}

delete_log_group() {
  local log_group="$1"

  if aws logs describe-log-groups \
    --log-group-name-prefix "${log_group}" \
    --query "logGroups[?logGroupName=='${log_group}'].logGroupName | [0]" \
    --output text | grep -qx "${log_group}"; then
    echo "Deleting log group ${log_group}"
    aws logs delete-log-group --log-group-name "${log_group}"
  else
    echo "Log group ${log_group} does not exist. Skipping."
  fi
}

delete_queue() {
  local queue_name="$1"
  local queue_url

  queue_url="$(aws sqs get-queue-url \
    --queue-name "${queue_name}" \
    --query "QueueUrl" \
    --output text 2>/dev/null || true)"

  if [[ -z "${queue_url}" || "${queue_url}" == "None" ]]; then
    echo "SQS queue ${queue_name} does not exist. Skipping."
    return
  fi

  echo "Deleting SQS queue ${queue_name}"
  aws sqs delete-queue --queue-url "${queue_url}" >/dev/null || true
}

delete_ecs_task_definitions() {
  local family_name="${NAME_PREFIX}-worker"
  local active_task_definitions
  local inactive_task_definitions
  local batch=()

  active_task_definitions="$(aws ecs list-task-definitions \
    --family-prefix "${family_name}" \
    --status ACTIVE \
    --query "taskDefinitionArns[]" \
    --output text)"

  for task_definition in ${active_task_definitions}; do
    echo "Deregistering ECS task definition ${task_definition}"
    aws ecs deregister-task-definition --task-definition "${task_definition}" >/dev/null || true
  done

  inactive_task_definitions="$(aws ecs list-task-definitions \
    --family-prefix "${family_name}" \
    --status INACTIVE \
    --query "taskDefinitionArns[]" \
    --output text)"

  if [[ -z "${inactive_task_definitions}" ]]; then
    echo "No inactive ECS task definitions found for ${family_name}."
    return
  fi

  echo "Deleting ECS task definitions for ${family_name}"
  for task_definition in ${inactive_task_definitions}; do
    batch+=("${task_definition}")
    if [[ "${#batch[@]}" -eq 10 ]]; then
      aws ecs delete-task-definitions --task-definitions "${batch[@]}" >/dev/null || true
      batch=()
    fi
  done

  if [[ "${#batch[@]}" -gt 0 ]]; then
    aws ecs delete-task-definitions --task-definitions "${batch[@]}" >/dev/null || true
  fi
}

delete_ecs_cluster() {
  local cluster_name="${NAME_PREFIX}-cluster"
  local cluster_status
  local running_tasks

  cluster_status="$(aws ecs describe-clusters \
    --clusters "${cluster_name}" \
    --query "clusters[0].status" \
    --output text 2>/dev/null || true)"

  if [[ -z "${cluster_status}" || "${cluster_status}" == "None" ]]; then
    echo "ECS cluster ${cluster_name} does not exist. Skipping."
    return
  fi

  running_tasks="$(aws ecs list-tasks \
    --cluster "${cluster_name}" \
    --desired-status RUNNING \
    --query "taskArns[]" \
    --output text 2>/dev/null || true)"

  for task_arn in ${running_tasks}; do
    echo "Stopping ECS task ${task_arn}"
    aws ecs stop-task \
      --cluster "${cluster_name}" \
      --task "${task_arn}" \
      --reason "Morphix post-destroy cleanup requested" >/dev/null || true
  done

  if [[ -n "${running_tasks}" ]]; then
    aws ecs wait tasks-stopped --cluster "${cluster_name}" --tasks ${running_tasks} || true
  fi

  echo "Deleting ECS cluster ${cluster_name}"
  aws ecs delete-cluster --cluster "${cluster_name}" >/dev/null || true
}

delete_lock_table() {
  local table_name="$1"

  if ! aws dynamodb describe-table --table-name "${table_name}" >/dev/null 2>&1; then
    echo "DynamoDB table ${table_name} does not exist. Skipping."
    return
  fi

  echo "Deleting DynamoDB table ${table_name}"
  aws dynamodb delete-table --table-name "${table_name}" >/dev/null
  aws dynamodb wait table-not-exists --table-name "${table_name}" || true
}

delete_log_group "/aws/ecs/containerinsights/${NAME_PREFIX}-cluster/performance"
delete_log_group "/aws/ecs/${NAME_PREFIX}-worker"
delete_log_group "/aws/lambda/${NAME_PREFIX}-api"
delete_queue "${NAME_PREFIX}-conversions"
delete_queue "${NAME_PREFIX}-conversions-dlq"
delete_ecs_task_definitions
delete_ecs_cluster
delete_lock_table "${LOCK_TABLE}"
delete_bucket "${STATE_BUCKET}"
