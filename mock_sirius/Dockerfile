FROM stoplight/prism:5.14.1
RUN apk update && apk upgrade
# TODO - remove below line once we can upgrade prism from 5.11.2
RUN npm upgrade jsonpath-plus --force && npm audit fix --force
COPY openapi.yml run.sh /app/
WORKDIR  /app
RUN chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]
