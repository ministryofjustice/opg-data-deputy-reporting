FROM stoplight/prism:4.14.1
COPY openapi.yml run.sh /app/
RUN apk upgrade libcrypto1.1 libssl1.1 busybox ssl_client zlib
WORKDIR  /app
RUN chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]
