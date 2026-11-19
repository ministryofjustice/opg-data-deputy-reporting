ARG FUNCTION_DIR=/function

FROM python:3.14.10-alpine3.24@sha256:5862d971d1f0ae26b258cefa4e893556b1d3aba81bd2ff30888704ad378bab67 AS base

# TODO Remove this once alpine upgrade available as it patches a vulnerability
RUN apk update && apk add --upgrade "zlib==1.4-r0"

RUN apk add --no-cache \
    libstdc++ \
    elfutils-dev

FROM base AS builder

RUN apk add --no-cache \
    build-base \
    libtool \
    autoconf \
    automake \
    cmake \
    libcurl

COPY --from=ghcr.io/astral-sh/uv@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff \
    /uv /uvx /usr/local/bin/

WORKDIR /build

COPY requirements/pyproject.toml .
COPY requirements/uv.lock .

RUN uv export --locked -o requirements.txt

RUN pip wheel \
    --wheel-dir /wheels \
    -r requirements.txt

FROM base AS runtime

ARG FUNCTION_DIR

WORKDIR ${FUNCTION_DIR}

COPY requirements/pyproject.toml /tmp/
COPY requirements/uv.lock /tmp/

COPY --from=builder /build/requirements.txt /tmp/
COPY --from=builder /wheels /wheels

RUN mkdir -p ${FUNCTION_DIR} && \
    pip install \
        --no-cache-dir \
        --no-index \
        --find-links=/wheels \
        --target ${FUNCTION_DIR} \
        -r /tmp/requirements.txt && \
    rm -rf /wheels /tmp/*

COPY functions/documents/app ./app

ENTRYPOINT ["python", "-m", "awslambdaric"]
CMD ["app.docs.lambda_handler"]