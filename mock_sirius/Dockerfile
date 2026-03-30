FROM stoplight/prism:5.15.0@sha256:bcea4f5dc44a6bccbbe86c2e6e16b6402fdf7a8da748ac4e48583a09f1d72924
#RUN apk update && apk upgrade && apk add --no-cache curl

#RUN rm -rf /usr/local/lib/node_modules/npm/node_modules/cross-spawn
#RUN npm install cross-spawn@7.0.5 --prefix /usr/local/lib/node_modules/npm/node_modules --no-save
#
## TODO: Remove the below mathod and use NPM when we are past 5.14.2
#RUN rm -rf /usr/src/prism/node_modules/jsonpath-plus
#RUN mkdir -p /usr/src/prism/node_modules/jsonpath-plus
#RUN curl -sL https://registry.npmjs.org/jsonpath-plus/-/jsonpath-plus-10.3.0.tgz | tar -xz -C /usr/src/prism/node_modules/jsonpath-plus --strip-components=1


RUN set -eux; \
    rm -rf /usr/local/lib/node_modules/npm; \
    rm -f /usr/local/bin/npm /usr/local/bin/npx; \
    rm -rf /root/.npm

COPY openapi.yml run.sh /app/
WORKDIR  /app
RUN chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]