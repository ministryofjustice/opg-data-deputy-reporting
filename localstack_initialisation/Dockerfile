FROM localstack/localstack:0.14@sha256:2f44dbb2af684c498892cfd6e493f2fea177edbf53322e0d6b28c28f32a454fb as localstack

RUN apt -yq install bash-completion bash

COPY ./test.pdf /tmp/test.pdf
COPY ./testCsv.csv /tmp/testCsv.csv
COPY ./init.sh /docker-entrypoint-initaws.d/init.sh
RUN chmod 544 /docker-entrypoint-initaws.d/init.sh