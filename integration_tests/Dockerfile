FROM python:3.10.7-alpine3.16 AS build
#Install the dependencies
RUN apk update && \
  apk add libpq-dev gcc python3-dev && \
  python3 -m venv /venv && \
  /venv/bin/pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN /venv/bin/pip install --disable-pip-version-check -r ./requirements.txt

COPY v2/ /app/integration_tests/v2/
ENV PYTHONPATH=/usr/local/lib/python3.10/site-packages:/app
WORKDIR /app/integration_tests/v2
ENTRYPOINT ["python", "-m", "pytest"]
