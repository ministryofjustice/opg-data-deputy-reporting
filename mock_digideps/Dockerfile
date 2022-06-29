FROM stoplight/prism:4
COPY openapi.yml run.sh /app/

RUN cd /app/ && chmod +x run.sh
# starts the mock server on port 5000
ENTRYPOINT ["/app/run.sh"]
