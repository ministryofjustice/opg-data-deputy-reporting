# our base image
FROM python:3.6-slim

COPY requirements.txt .
COPY deputy-reporting-openapi.yml .

COPY requirements.txt .
COPY sirius_public_api.yml .
COPY app.py .

RUN pip install -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV='development'

CMD ["python", "app.py"]
