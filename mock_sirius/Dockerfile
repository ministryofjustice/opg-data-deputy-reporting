FROM stoplight/prism:5.15.0@sha256:bcea4f5dc44a6bccbbe86c2e6e16b6402fdf7a8da748ac4e48583a09f1d72924

# Patch lodash in-place (TO REMOVE)
RUN set -eux; \
    npm install -g lodash@4.18.1; \
    npm ls -g lodash

# Get rid of NPM entirely as not needed after install
RUN set -eux; \
    rm -rf /usr/local/lib/node_modules/npm; \
    rm -f /usr/local/bin/npm /usr/local/bin/npx; \
    rm -rf /root/.npm

COPY openapi.yml run.sh /app/
WORKDIR  /app
RUN chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]