FROM stoplight/prism:5.14.2
RUN apk update && apk upgrade && apk add --no-cache curl

RUN rm -rf /usr/local/lib/node_modules/npm/node_modules/cross-spawn
RUN npm install cross-spawn@7.0.5 --prefix /usr/local/lib/node_modules/npm/node_modules --no-save

COPY openapi.yml run.sh /app/
WORKDIR  /app
RUN chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]