# === BUILD IMAGE ===
FROM python:3.14-slim@sha256:cea0e6040540fb2b965b6e7fb5ffa00871e632eef63719f0ea54bca189ce14a6 AS builder
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
FROM python:3.14-slim@sha256:cea0e6040540fb2b965b6e7fb5ffa00871e632eef63719f0ea54bca189ce14a6
# Copy only the installed packages from the previous stage to the working directory
COPY --from=builder /app /app
ENV PYTHONPATH=/app

WORKDIR /app/integration_tests/v2
# Set the entrypoint for the unit tests
ENTRYPOINT ["python", "-m", "pytest"]
