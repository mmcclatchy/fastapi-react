FROM python:3-slim AS builder

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install poetry

COPY . .

VOLUME [ "./app" ]

FROM builder as dev-envs

RUN apt-get update && apt-get install -y --no-install-recommends git curl

RUN useradd -ms /bin/bash myuser

USER myuser

RUN poetry install

# # Set the development command if ENVIRONMENT is set to development
# RUN if [ "$ENVIRONMENT" = "development" ]; then echo "Running in development mode"; fi
CMD ["poetry", "run", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]
