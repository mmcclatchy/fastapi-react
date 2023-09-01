# Use an official Python runtime as the base image
FROM python:3-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Install the Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install poetry

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock ./

# Install the dependencies using Poetry
RUN poetry install --no-root

# Copy the source code to the container
COPY . .

VOLUME [ "./app" ]

FROM builder as dev-envs

RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends git
EOF

RUN <<EOF
useradd -s /bin/bash -m vscode
groupadd docker
usermod -aG docker vscode
EOF

# # Set the command to run the FastAPI app
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# # Set the development command if ENVIRONMENT is set to development
# RUN if [ "$ENVIRONMENT" = "development" ]; then echo "Running in development mode"; fi
CMD ["poetry", "run", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]
