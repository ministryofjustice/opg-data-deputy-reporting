# === BUILD IMAGE ===
FROM python:3.14-slim@sha256:c845af9399020c7e562969a13689e929074a10fd057acd1b1fad06a2fb068e97 AS builder
# Set the working directory to /app
WORKDIR /app
# Copy the requirements file to the working directory
COPY requirements.txt requirements.txt
# Pip dependency installs
RUN python -m pip install --upgrade pip
RUN python -m pip install \
        --target /app \
        --requirement requirements.txt
COPY v2/ /app/integration_tests/v2/

# === FINAL IMAGE ===
FROM python:3.14-slim@sha256:c845af9399020c7e562969a13689e929074a10fd057acd1b1fad06a2fb068e97
# Copy only the installed packages from the previous stage to the working directory
COPY --from=builder /app /app
ENV PYTHONPATH=/app

WORKDIR /app/integration_tests/v2
# Set the entrypoint for the unit tests
ENTRYPOINT ["python", "-m", "pytest"]
