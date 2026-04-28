FROM stoplight/prism:5.15.10@sha256:586d1f0f94f8d0eaf20b26b8b41f985f2a2d494bea297bd3988c3de3eb87094e

# Get rid of NPM entirely as not needed after install
RUN set -eux; \
    rm -rf /usr/local/lib/node_modules/npm; \
    rm -f /usr/local/bin/npm /usr/local/bin/npx; \
    rm -rf /root/.npm

COPY openapi.yml run.sh /app/
WORKDIR  /app
RUN chmod +x run.sh
ENTRYPOINT ["/app/run.sh"]