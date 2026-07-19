[English](README.md) | [Español](README.es.md)

# Morphix

Web app for asynchronous file conversion without external conversion APIs. React/Vite frontend, FastAPI API, Python conversion worker, Terraform/Terragrunt infrastructure, and GitHub Actions deployments.

Licensed under the [Apache License 2.0](LICENSE).

## Local usage

To run the complete system locally with Docker Compose:

```bash
docker compose up --build
```

The full system runs locally on Docker Compose: frontend (Vite dev with HMR), FastAPI API on uvicorn with reload, conversion worker consuming Redis, SQLite for state, and a shared filesystem for files. The local backend uses independent adapters; the AWS backend keeps its DynamoDB, S3, SQS, Step Functions, and Streams adapters unchanged.

```mermaid
flowchart LR
    Browser["Browser (Vite :5173)"] -->|HTTP + X-User-Id| API["FastAPI :8000<br/>uvicorn --reload"]
    Browser <-->|WebSocket /ws| API
    Browser -->|local token PUT/GET| API
    API -->|SQLite + filesystem| Local["Local volume<br/>SQLite + files"]
    API -->|publish events| Redis[("Redis")]
    Worker["Worker<br/>queue_worker"] -->|consume stream| Redis
    Worker -->|read/write| Local
    Worker -->|convert| LocalBin["LibreOffice / FFmpeg / ImageMagick"]
    Worker -->|write output + mark COMPLETED| Local
```

1. Open http://localhost:5173. The frontend ships with a synthetic `runtime-config.json` that wires it to the API at `http://localhost:8000` and the realtime WebSocket at `ws://localhost:8000/ws`.
2. Upload a supported file from the UI. The API issues a temporary local URL and stores the file in the shared filesystem.
3. Start the conversion. The local `RedisConversionOrchestrator` publishes the job to a Redis Stream and marks it `QUEUED` in SQLite — no Step Functions needed.
4. The worker consumes the message, runs the conversion pipeline (read → convert → write), and persists `PROCESSING → COMPLETED` (or `FAILED`) in SQLite.
5. The API and worker publish events through Redis Pub/Sub; the API forwards them over WebSocket, so the UI updates in realtime.

Hot-reload applies to the API (`uvicorn --reload`) and the frontend (Vite HMR). To apply worker changes, run `docker compose restart worker`. Use `docker compose down -v` to wipe SQLite, local files, and Redis; `docker compose down` keeps them persisted in the volume.

API docs: http://localhost:8000/docs. The `X-User-Id` header (any string ≤128 chars) identifies the job owner and is stored in `localStorage` between sessions.

## Architecture

Four explicit boundaries: frontend owns the user workflow, API owns job coordination and security, worker owns conversion execution, infrastructure owns deployment, isolation, storage and observability.

```mermaid
flowchart LR
    Browser["Browser (React/Vite)"] --> CF["CloudFront + S3"]
    Browser -->|HTTP| AGW["API Gateway"]
    AGW --> Lambda["FastAPI Lambda"]
    Lambda --> DDB[("DynamoDB jobs")]
    Lambda -->|presigned URL| S3I[("S3 input")]
    Lambda -->|start| SFN{{"Step Functions"}}
    SFN -->|enqueue| SQS[("SQS + DLQ")]
    SQS --> ECS["ECS Fargate worker"]
    ECS -->|download| S3I
    ECS -->|convert| LocalBin["LibreOffice / FFmpeg / ImageMagick"]
    ECS -->|upload| S3O[("S3 output")]
    ECS -->|callback| SFN
    Lambda -->|presigned URL| S3O
```

The runtime path is asynchronous: the frontend is delivered from S3 through CloudFront, the API receives job requests through API Gateway/Lambda, Step Functions orchestrates each conversion, SQS buffers worker execution, and one ECS Fargate worker consumes the queue sequentially. The browser never receives AWS credentials; it reads `runtime-config.json` published by Terraform to discover the API base URL and uses presigned URLs to move files directly to/from S3.

### Frontend — Feature-Sliced Design

`apps/frontend/src` (React 19 + Vite + Tailwind v4 + shadcn/ui, server state via TanStack Query):

```mermaid
flowchart LR
    app["app<br/>providers · router · styles"]
    pages["pages<br/>converter"]
    widgets["widgets<br/>workspace · overview · jobs-history · app-shell"]
    features["features<br/>convert · select-format · download · delete-job"]
    entities["entities<br/>job · conversion · user"]
    shared["shared<br/>api · config · ui · lib"]
    app --> pages --> widgets --> features --> entities --> shared
```

- `app`: bootstrapping, providers, router, global styles.
- `pages`: route-level compositions.
- `widgets`: complete UI blocks (conversion workspace, overview, jobs history).
- `features`: user actions with business intent (convert file, select target format, download result, delete job).
- `entities`: domain-facing frontend models (jobs, conversions, user context).
- `shared`: HTTP client, env config, hooks, UI primitives, utilities, types.

### API — Hexagonal Architecture

`apps/api/src/morphix_api` (FastAPI). Inbound adapters call use cases, use cases depend on ports, outbound adapters implement those ports. The core never depends on FastAPI or AWS SDK details.

```mermaid
flowchart RL
    HTTP["adapters/inbound/http<br/>FastAPI routes · schemas · DI"] --> UC["application/use_cases<br/>create · list · urls · start · delete"]
    UC --> PORTS["application/ports<br/>job repo · object urls · orchestration"]
    OUT["adapters/outbound<br/>DynamoDB · S3 presigned · Step Functions"] -.->|implements| PORTS
    UC --> DOMAIN["domain<br/>concepts · value objects · policies · errors"]
    CORE["core<br/>config · security · time"] --> UC
```

### Worker — Pipeline-Oriented Clean Architecture

`apps/worker/src/morphix_worker` (Python on ECS Fargate). The conversion lifecycle is an explicit pipeline: load job → mark processing → download input → convert → upload output → persist status. Failure handling is part of the pipeline, not hidden in adapters.

```mermaid
flowchart LR
    EP["entrypoints<br/>ECS env parsing"] --> PIPE["application/pipeline<br/>step orchestration · error flow"]
    PIPE --> WPORTS["application/ports<br/>object storage · job repo · converter · workspace"]
    PIPE --> WDOMAIN["domain<br/>job · result · format · status · policies"]
    CONV["converters<br/>LibreOffice · FFmpeg · ImageMagick · spreadsheets · PDF"] -.->|implements| WPORTS
    WOUT["adapters/outbound<br/>S3 · DynamoDB"] -.->|implements| WPORTS
    WCORE["core<br/>config · logging · workspace · subprocess"] --> PIPE
```

The pipeline depends on ports, not on S3, DynamoDB, ECS or specific binaries — keeping conversion logic testable and infrastructure concerns at the edge.

### Infrastructure — AWS Runtime and Delivery

Provisioned with Terraform modules (`infra/blueprints/modules`) and Terragrunt live stacks (`infra/terraform`). GitHub Actions builds, tests and deploys frontend, API Lambda packages, worker images and infrastructure changes.

- CloudFront + S3 deliver the frontend.
- API Gateway invokes the FastAPI Lambda adapter.
- Private S3 buckets store input/output via short-lived presigned URLs.
- Step Functions owns orchestration, status transitions and worker callbacks.
- SQS buffers jobs, retries pickup failures, moves poison messages to a DLQ.
- ECS Fargate runs the worker from ECR (`desired_count = 1`).
- DynamoDB stores job metadata, ownership and status.
- CloudWatch captures logs and telemetry.
- Frontend runtime variables are not injected by workflows; Terraform publishes them as S3 runtime config.

## Repository Layout

- `apps/frontend`: Bun-managed React + TypeScript + Vite conversion UI.
- `apps/api`: FastAPI Lambda service for jobs, batches, presigned URLs, ownership checks and Step Functions starts.
- `apps/worker`: Dockerized Python worker using local conversion engines.
- `infra/blueprints`: reusable Terraform modules and remote-state bootstrap. The state machine lives in the API module and publishes work to the shared conversion queue.
- `infra/terraform`: Terragrunt live stacks.
- `.github/workflows`: CI/CD for infra, frontend and backend. API and worker deploy from one ordered backend workflow.
- `docs/prd-coverage.md`: PRD requirement coverage checklist.

No `Taskfile.yml` by design, matching MVP scope.

## MVP Limits

- Max upload size: configurable, default `100 MB`.
- Input retention: `1 day`. Output retention: `7 days`.
- Worker timeout: configurable, default `900 seconds`.
- Conversion engines are local binaries or Python libraries packaged in the worker image.

## Deploy

1. Configure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as repository secrets. `AWS_REGION` is fixed in workflows as `us-east-1`.
2. Run `.github/workflows/infra-lifecycle.yml` with `plan` or `apply`. Bootstraps the Terraform state bucket and DynamoDB lock table if missing. Destroy flows stop running conversions and empty project buckets/ECR images before Terragrunt destroys stacks.
3. Deploy backend through `.github/workflows/backend-deploy.yml`, selecting `api`, `worker` or `both`. On push, it detects path changes and deploys only the affected components. The API Lambda is packaged with `apps/api/scripts/build_lambda.sh` (function zip + dependencies zip as a Lambda Layer); the worker is a Docker/ECR image for ECS Fargate.

Terraform modules use private S3 buckets, short-lived presigned URLs, DynamoDB TTL, CloudWatch logs, Step Functions callbacks, SQS redrive policies, ECS Fargate isolation, and separated state boundaries.
