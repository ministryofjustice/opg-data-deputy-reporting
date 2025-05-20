FROM stoplight/prism:5.14.2
RUN apk update && apk upgrade
COPY openapi.yml run.sh /app/
WORKDIR  /app
RUN chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]