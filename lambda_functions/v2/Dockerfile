# Define function directory
ARG FUNCTION_DIR="/function"

FROM python:3.12-alpine3.22 AS python-alpine
RUN apk add --no-cache \
    libstdc++ \
    elfutils-dev

RUN apk update && apk upgrade

FROM python-alpine as build-image

# Install aws-lambda-cpp build dependencies
RUN apk add --no-cache \
    build-base \
    libtool \
    autoconf \
    automake \
    make \
    cmake \
    libcurl

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy function code
COPY functions/documents/app ${FUNCTION_DIR}/app

COPY requirements/requirements.txt requirements.txt

# Install the runtime interface client
RUN python -m pip install --upgrade pip
RUN python -m pip install \
        --target ${FUNCTION_DIR} \
        --requirement requirements.txt

# Multi-stage build: grab a fresh copy of the base image
FROM python-alpine
# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the build image dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "app.docs.lambda_handler" ]
