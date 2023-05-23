FROM python:3.10.7-alpine3.16
#Install the dependencies
RUN apk update && \
  apk add libpq-dev gcc python3-dev py3-pip

COPY requirements.txt requirements.txt
RUN pip3 install --disable-pip-version-check -r ./requirements.txt

COPY v2/ /app/integration_tests/v2/
ENV PYTHONPATH=/usr/local/lib/python3.10/site-packages:/app
WORKDIR /app/integration_tests/v2
ENTRYPOINT ["python3", "-m", "pytest"]
