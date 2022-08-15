FROM stoplight/prism:4
COPY openapi.yml run.sh /app/
RUN apk upgrade libcrypto1.1 libssl1.1 busybox ssl_client zlib
RUN cd /app/ && chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]
