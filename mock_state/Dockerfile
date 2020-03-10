# our base image
FROM python:3.6-slim

COPY requirements.txt .
COPY app.py .

RUN pip install -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV='development'

CMD ["python", "app.py"]
