FROM stoplight/prism:5.3.2
COPY openapi.yml run.sh /app/

RUN cd /app/ && chmod +x run.sh
# starts the mock server on port 5000
ENTRYPOINT ["/app/run.sh"]
