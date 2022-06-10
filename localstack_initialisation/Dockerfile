FROM localstack/localstack:0.14 as localstack

COPY ./main /tmp/localstack/main
COPY ./test.pdf /tmp/test.pdf
COPY ./init.sh /docker-entrypoint-initaws.d/init.sh
RUN chmod 544 /docker-entrypoint-initaws.d/init.sh