FROM stoplight/prism:5.15.1@sha256:d7dd4504976390636b1ac162530ddaaa220b8850e208b1a68519e815c47a3d35

# Get rid of NPM entirely as not needed after install
RUN set -eux; \
    rm -rf /usr/local/lib/node_modules/npm; \
    rm -f /usr/local/bin/npm /usr/local/bin/npx; \
    rm -rf /root/.npm

COPY openapi.yml run.sh /app/
WORKDIR  /app
RUN chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]