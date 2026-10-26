# === BUILD IMAGE ===
FROM python:3.14.9-slim@sha256:35caba83af2fe6da9a5d922f9b0156f21d1246a48278c58a08bd253303ba42e8 AS builder
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
FROM python:3.14.9-slim@sha256:35caba83af2fe6da9a5d922f9b0156f21d1246a48278c58a08bd253303ba42e8
# Copy only the installed packages from the previous stage to the working directory
COPY --from=builder /app /app
ENV PYTHONPATH=/app

WORKDIR /app/integration_tests/v2
# Set the entrypoint for the unit tests
ENTRYPOINT ["python", "-m", "pytest"]
