#!/usr/bin/env bash
set -euo pipefail

NAME_PREFIX="${PROJECT_NAME}-${ENVIRONMENT}"

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

stop_state_machine_executions() {
  local state_machine_name="${NAME_PREFIX}-conversion"
  local state_machine_arn
  local running_executions

  state_machine_arn="$(aws stepfunctions list-state-machines \
    --query "stateMachines[?name=='${state_machine_name}'].stateMachineArn | [0]" \
    --output text 2>/dev/null || true)"

  if [[ -z "${state_machine_arn}" || "${state_machine_arn}" == "None" ]]; then
    echo "State machine ${state_machine_name} does not exist. Skipping running executions cleanup."
    return
  fi

  running_executions="$(aws stepfunctions list-executions \
    --state-machine-arn "${state_machine_arn}" \
    --status-filter RUNNING \
    --query "executions[].executionArn" \
    --output text)"

  if [[ -z "${running_executions}" ]]; then
    echo "No running Step Functions executions found."
    return
  fi

  for execution_arn in ${running_executions}; do
    echo "Stopping Step Functions execution ${execution_arn}"
    aws stepfunctions stop-execution \
      --execution-arn "${execution_arn}" \
      --cause "Morphix infrastructure destroy requested" >/dev/null || true
  done

  for _ in {1..30}; do
    running_executions="$(aws stepfunctions list-executions \
      --state-machine-arn "${state_machine_arn}" \
      --status-filter RUNNING \
      --query "executions[].executionArn" \
      --output text)"

    if [[ -z "${running_executions}" ]]; then
      echo "All Step Functions executions are stopped."
      return
    fi

    sleep 10
  done

  echo "Some Step Functions executions are still stopping. Continuing with Terraform destroy."
}

stop_worker_tasks() {
  local cluster_name="${NAME_PREFIX}-cluster"
  local family_name="${NAME_PREFIX}-worker"
  local cluster_status
  local task_arns

  cluster_status="$(aws ecs describe-clusters \
    --clusters "${cluster_name}" \
    --query "clusters[0].status" \
    --output text 2>/dev/null || true)"

  if [[ "${cluster_status}" != "ACTIVE" ]]; then
    echo "ECS cluster ${cluster_name} is not active. Skipping worker task cleanup."
    return
  fi

  task_arns="$(aws ecs list-tasks \
    --cluster "${cluster_name}" \
    --desired-status RUNNING \
    --family "${family_name}" \
    --query "taskArns[]" \
    --output text)"

  if [[ -z "${task_arns}" ]]; then
    echo "No running worker tasks found."
    return
  fi

  for task_arn in ${task_arns}; do
    echo "Stopping ECS task ${task_arn}"
    aws ecs stop-task \
      --cluster "${cluster_name}" \
      --task "${task_arn}" \
      --reason "Morphix infrastructure destroy requested" >/dev/null || true
  done

  aws ecs wait tasks-stopped --cluster "${cluster_name}" --tasks ${task_arns} || true
}

empty_worker_repository() {
  local repository_name="${NAME_PREFIX}-worker"
  local images_file
  local chunk_dir
  local image_count

  if ! aws ecr describe-repositories --repository-names "${repository_name}" >/dev/null 2>&1; then
    echo "ECR repository ${repository_name} does not exist. Skipping."
    return
  fi

  images_file="$(mktemp)"
  chunk_dir="$(mktemp -d)"
  aws ecr list-images --repository-name "${repository_name}" --query "imageIds" --output json > "${images_file}"

  image_count="$(python3 - "${images_file}" "${chunk_dir}" <<'PY'
import json
import pathlib
import sys

images_file = pathlib.Path(sys.argv[1])
chunk_dir = pathlib.Path(sys.argv[2])
images = json.loads(images_file.read_text())

for index in range(0, len(images), 100):
    (chunk_dir / f"images-{index // 100}.json").write_text(json.dumps(images[index:index + 100]))

print(len(images))
PY
)"

  if [[ "${image_count}" == "0" ]]; then
    rm -f "${images_file}"
    rm -rf "${chunk_dir}"
    echo "ECR repository ${repository_name} has no images."
    return
  fi

  echo "Deleting images from ECR repository ${repository_name}"
  for image_ids_file in "${chunk_dir}"/images-*.json; do
    [[ -e "${image_ids_file}" ]] || continue
    aws ecr batch-delete-image \
      --repository-name "${repository_name}" \
      --image-ids "file://${image_ids_file}" >/dev/null || true
  done

  rm -f "${images_file}"
  rm -rf "${chunk_dir}"
}

stop_state_machine_executions
stop_worker_tasks
empty_bucket "${FRONTEND_BUCKET_NAME:-${NAME_PREFIX}-frontend}"
empty_bucket "${INPUT_BUCKET_NAME:-${NAME_PREFIX}-input}"
empty_bucket "${OUTPUT_BUCKET_NAME:-${NAME_PREFIX}-output}"
empty_worker_repository
