# === BUILD IMAGE ===
FROM python:3.15.0-slim@sha256:f5b92f2a669a4c347044f29367f31983280b648250ca94dea66f98c53bc87e58 AS builder
# Set the working directory to /app
WORKDIR /app

# Install the runtime interface client
COPY --from=ghcr.io/astral-sh/uv@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff /uv /uvx /bin/
COPY uv.lock .
COPY pyproject.toml .
RUN uv export --locked -o requirements.txt \
    && python -m pip install --no-cache-dir \
    --target /app \
    -r requirements.txt

COPY v2/ /app/integration_tests/v2/

# === FINAL IMAGE ===
FROM python:3.15.0-slim@sha256:f5b92f2a669a4c347044f29367f31983280b648250ca94dea66f98c53bc87e58
# Copy only the installed packages from the previous stage to the working directory
COPY --from=builder /app /app
ENV PYTHONPATH=/app

WORKDIR /app/integration_tests/v2
# Set the entrypoint for the unit tests
ENTRYPOINT ["python", "-m", "pytest"]
