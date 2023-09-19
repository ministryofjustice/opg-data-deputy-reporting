FROM stoplight/prism:5.3.2
COPY openapi.yml run.sh /app/
#RUN apk upgrade libcrypto1.1 libssl1.1 busybox ssl_client zlib
WORKDIR  /app
RUN chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]
