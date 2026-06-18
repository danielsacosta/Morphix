# Morphix PRD Coverage

This checklist maps the PRD to implemented repository assets.

## Product And Architecture

| PRD area | Coverage |
| --- | --- |
| Monorepo | Root workspace with `apps`, `infra`, `.github`, `docs`. |
| Frontend React + Vite | `apps/frontend`. |
| Backend separated from infra | `apps/api`, deployed by `infra/blueprints/modules/api`. |
| Worker in ECS Fargate | `apps/worker`, `infra/blueprints/modules/fargate-worker`. |
| Step Functions orchestration | `infra/blueprints/modules/step-functions`. |
| S3 input/output/frontend | `storage` and `frontend` modules. |
| DynamoDB jobs table | `jobs-db` module. |
| CI/CD GitHub Actions | `.github/workflows/*.yml`. |
| No Taskfile/local Docker Compose | No `Taskfile.yml` or Docker Compose is included. |

## Functional Requirements

| ID | Status | Evidence |
| --- | --- | --- |
| RF-01 | Covered | Frontend file picker and direct upload flow in `apps/frontend/src/App.tsx`. |
| RF-02 | Covered | Format selector uses `SUPPORTED_CONVERSIONS` from `apps/frontend/src/conversions.ts`. |
| RF-03 | Covered | `POST /jobs` in `apps/api/src/morphix_api/main.py`. |
| RF-04 | Covered | `POST /jobs/{job_id}/upload-url`. |
| RF-05 | Covered | Frontend uploads using the presigned PUT URL. |
| RF-06 | Covered | `POST /jobs/{job_id}/start` starts Step Functions. |
| RF-07 | Covered | State machine uses `arn:aws:states:::ecs:runTask.sync`. |
| RF-08 | Covered | Worker downloads input from S3 in `apps/worker/src/morphix_worker/storage.py`. |
| RF-09 | Covered | Worker converters use LibreOffice, FFmpeg, ImageMagick and Python libraries; no external conversion API. |
| RF-10 | Covered | Worker uploads converted result to S3. |
| RF-11 | Covered | Worker updates DynamoDB status on completion/failure. |
| RF-12 | Covered | Frontend polls `GET /jobs/{job_id}`. |
| RF-13 | Covered | `GET /jobs/{job_id}/download-url`. |
| RF-14 | Covered | `GET /jobs` and frontend history section. |
| RF-15 | Covered | API/worker persist `error_message`; infra sends logs to CloudWatch. |
| RF-16 | Covered | API validates `MAX_FILE_SIZE_MB`; frontend mirrors visible max size. |
| RF-17 | Covered | API validates allowed source/target conversion pairs. |
| RF-18 | Covered | API requires `X-User-Id` and checks job ownership before every job action. |

## Non-Functional Requirements

| ID | Status | Evidence |
| --- | --- | --- |
| RNF-01 | Covered | Step Functions + ECS asynchronous flow. |
| RNF-02 | Covered | S3 modules block public access and avoid public ACLs. |
| RNF-03 | Covered | API returns short-lived presigned URLs. |
| RNF-04 | Covered | Terraform modules plus Terragrunt live stacks. |
| RNF-05 | Covered | Worker task definition uses Fargate. |
| RNF-06 | Covered | Log groups for API, worker and Step Functions. |
| RNF-07 | Covered | State machine retry/catch and worker timeout controls. |
| RNF-08 | Covered | S3 lifecycle rules and DynamoDB TTL. |
| RNF-09 | Covered | Frontend module provisions CloudFront. |
| RNF-10 | Covered | Separate `frontend`, `api`, `worker`, and infra modules/stacks. |
| RNF-11 | Covered | Four deployment workflows plus infra lifecycle and scheduled destroy. |
| RNF-12 | Covered | `destroy-infra-scheduled.yml` and infra lifecycle destroy action. |

## MVP Conversions

| Category | Pairs |
| --- | --- |
| Documents | DOCX->PDF, XLSX->PDF, PPTX->PDF, PDF->DOCX, CSV->XLSX, XLSX->CSV |
| Images | PNG->JPG, JPG->PNG, JPG->WEBP, PNG->WEBP |
| Audio/video | MP4->MP3, MP4->WEBM, MOV->MP4, WAV->MP3, MP3->WAV |

## Security And Operations

| Requirement | Coverage |
| --- | --- |
| Private buckets and encryption | `frontend` and `storage` modules. |
| Least-privilege roles | API and worker modules grant scoped S3/DynamoDB/Step Functions permissions. |
| MIME/extension validation | API format validation and frontend accepted extensions. |
| Logs without sensitive file content | API/worker log job ids, statuses and errors only. |
| Separate input/output buckets | `storage` module. |
| CloudWatch dashboards and alarms | `observability` module. |
| Configurable limits | Environment variables and Terraform inputs. |

