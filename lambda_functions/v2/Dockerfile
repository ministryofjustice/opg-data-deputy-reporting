### Base image - contains dependencies required for build
FROM public.ecr.aws/lambda/python:3.7 AS base

# fixes security issues detected in build.
RUN yum update -y rpm openssl nss nss-util nss-softokn nspr expat cyrus-sasl-lib

# Install Python dependencies for worker
COPY requirements/requirements.txt /app/
RUN pip install -r /app/requirements.txt --target ${LAMBDA_TASK_ROOT}

### Final image - contains compiled dependencies
FROM public.ecr.aws/lambda/python:3.7 as production

# fixes security issues detected in build.
RUN yum update -y rpm openssl nss nss-util nss-softokn nspr urllib3 \
    xz-libs xz python27-libs python27 gzip expat

COPY --from=base ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}
COPY functions/documents/app ${LAMBDA_TASK_ROOT}/app

CMD [ "app.docs.lambda_handler" ]