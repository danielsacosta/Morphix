FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

CMD ["morphix_api.main.handler"]

