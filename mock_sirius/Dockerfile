FROM stoplight/prism:4
COPY openapi.yml run.sh /app/
RUN libcrypto1.1
RUN cd /app/ && chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]
