# === BUILD IMAGE ===
FROM python:3.14.7-slim@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d AS builder
# Set the working directory to /app
WORKDIR /app

# Install the runtime interface client
COPY --from=ghcr.io/astral-sh/uv@sha256:2bb3ebca0a796a155094a27773d290c4b074572e6107f171d88d086682fd2500 /uv /uvx /bin/
COPY uv.lock .
COPY pyproject.toml .
RUN uv export --locked -o requirements.txt \
    && python -m pip install --no-cache-dir \
    --target /app \
    -r requirements.txt

COPY v2/ /app/integration_tests/v2/

# === FINAL IMAGE ===
FROM python:3.14.7-slim@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d
# Copy only the installed packages from the previous stage to the working directory
COPY --from=builder /app /app
ENV PYTHONPATH=/app

WORKDIR /app/integration_tests/v2
# Set the entrypoint for the unit tests
ENTRYPOINT ["python", "-m", "pytest"]
