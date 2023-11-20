FROM stoplight/prism:5.5.1
COPY openapi.yml run.sh /app/
WORKDIR  /app
RUN chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]
