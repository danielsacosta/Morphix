# Morphix API

FastAPI service responsible for conversion job lifecycle, batch creation, storage URLs, orchestration, and user ownership checks. The application selects local SQLite/filesystem/Redis adapters through `RUNTIME_BACKEND=local` and keeps the AWS adapters available through `RUNTIME_BACKEND=aws`.

## Endpoints

- `GET /health`
- `POST /jobs`
- `POST /jobs/batch`
- `GET /jobs`
- `GET /jobs/{job_id}`
- `POST /jobs/{job_id}/upload-url`
- `POST /jobs/{job_id}/start`
- `GET /jobs/{job_id}/download-url`
- `DELETE /jobs/{job_id}`

Every job endpoint requires `X-User-Id`. This MVP keeps identity simple while enforcing ownership boundaries in the API.
