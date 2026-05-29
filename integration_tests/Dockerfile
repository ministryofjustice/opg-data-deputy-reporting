# === BUILD IMAGE ===
FROM python:3.13-slim@sha256:b04b5d7233d2ad9c379e22ea8927cd1378cd15c60d4ef876c065b25ea8fb3bf3 AS builder
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
FROM python:3.13-slim@sha256:b04b5d7233d2ad9c379e22ea8927cd1378cd15c60d4ef876c065b25ea8fb3bf3
# Copy only the installed packages from the previous stage to the working directory
COPY --from=builder /app /app
ENV PYTHONPATH=/app

WORKDIR /app/integration_tests/v2
# Set the entrypoint for the unit tests
ENTRYPOINT ["python", "-m", "pytest"]
