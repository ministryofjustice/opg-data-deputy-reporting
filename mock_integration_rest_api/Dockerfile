# === BUILD IMAGE ===
FROM python:3.12-slim AS builder
# Set the working directory to /app
WORKDIR /app
# Copy the requirements file to the working directory
COPY mock_integration_rest_api/requirements.txt requirements.txt
# Pip dependency installs
RUN python -m pip install --upgrade pip
RUN python -m pip install \
        --target /app \
        --requirement requirements.txt
COPY lambda_functions/v2/functions /app/lambda_functions/v2/functions
COPY mock_integration_rest_api /app/mock_integration_rest_api

# === FINAL IMAGE ===
FROM python:3.12-slim
WORKDIR /app
# Copy only the installed packages from the previous stage to the working directory
COPY --from=builder /app /app
ENV PYTHONPATH=/app
# Set the entrypoint for the unit tests
CMD ["python", "./mock_integration_rest_api/app.py"]
