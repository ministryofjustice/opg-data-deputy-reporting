# our base image
FROM python:3.8-slim

WORKDIR /var/www/
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /var/www/mock_sirius_backend/
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["python", "mock_sirius_backend/app.py"]
