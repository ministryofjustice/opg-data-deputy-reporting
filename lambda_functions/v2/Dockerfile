ARG FUNCTION_DIR=/function

FROM python:3.14.8-alpine3.24@sha256:f6a589d43c42b9e7f7dc67a12d37132491f362859a5d750607710cc56da3bc72 AS base

# Temporary workaround until Alpine ships the patched package
RUN apk update && apk add --upgrade "zlib=1.3.2-r1"

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

COPY --from=ghcr.io/astral-sh/uv@sha256:61d393e44e249f2e4b526b6c7ddcecce245946826e608e11c93ad4f5bba55b21 \
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