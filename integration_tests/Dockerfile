FROM debian:buster-slim AS build
#Install the dependencies
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-venv libpq-dev gcc libpython3-dev && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN /venv/bin/pip install --disable-pip-version-check -r ./requirements.txt

FROM gcr.io/distroless/python3-debian11
#Define the user-id and copy the packages from the previous builds
USER 1001
COPY --chown=1001:1001 --from=build /venv/lib/python3.7/site-packages/ /usr/local/lib/python3.7/site-packages
COPY --chown=1001:1001 v2/ /app/integration_tests/v2/
ENV PYTHONPATH=/usr/local/lib/python3.7/site-packages:/app
WORKDIR /app/integration_tests/v2
ENTRYPOINT ["python", "-m", "pytest"]