# Morphix API

FastAPI service responsible for conversion job lifecycle, presigned S3 URLs, Step Functions orchestration, and user ownership checks.

## Endpoints

- `GET /health`
- `POST /jobs`
- `GET /jobs`
- `GET /jobs/{job_id}`
- `POST /jobs/{job_id}/upload-url`
- `POST /jobs/{job_id}/start`
- `GET /jobs/{job_id}/download-url`
- `DELETE /jobs/{job_id}`

Every job endpoint requires `X-User-Id`. This MVP keeps identity simple while enforcing ownership boundaries in the API.

