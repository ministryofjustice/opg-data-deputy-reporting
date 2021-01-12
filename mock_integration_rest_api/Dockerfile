# our base image
FROM python:3.8-slim

WORKDIR /var/www/
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONPATH=/var/www
CMD ["python", "mock_integration_rest_api/app.py"]
