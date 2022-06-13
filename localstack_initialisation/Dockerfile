FROM localstack/localstack:0.14 as localstack

RUN apt -yq install bash-completion bash

COPY ./test.pdf /tmp/test.pdf
COPY ./testCsv.csv /tmp/testCsv.csv
COPY ./init.sh /docker-entrypoint-initaws.d/init.sh
RUN chmod 544 /docker-entrypoint-initaws.d/init.sh