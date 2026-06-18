FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /usr/local/bin/uv
COPY pyproject.toml README.md ./
COPY src ./src

RUN uv pip install --system --no-cache .

CMD ["morphix_api.main.handler"]
