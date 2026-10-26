ARG FUNCTION_DIR=/function

FROM python:3.14.9-alpine3.24@sha256:dbeb11d16bb95c3a7e3c25c842cb9f20cbc8c18f8be0461a4a0dcc861ad386a0 AS base

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