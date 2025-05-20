FROM stoplight/prism:5.14.2
RUN apk update && apk upgrade && apk add --no-cache curl

RUN rm -rf /usr/local/lib/node_modules/npm/node_modules/cross-spawn
RUN npm install cross-spawn@7.0.5 --prefix /usr/local/lib/node_modules/npm/node_modules --no-save

RUN rm -rf /usr/src/prism/node_modules/jsonpath-plus
RUN mkdir -p /usr/src/prism/node_modules/jsonpath-plus
RUN curl -sL https://registry.npmjs.org/jsonpath-plus/-/jsonpath-plus-10.3.0.tgz | tar -xz -C /usr/src/prism/node_modules/jsonpath-plus --strip-components=1

COPY openapi.yml run.sh /app/
WORKDIR  /app
RUN chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]