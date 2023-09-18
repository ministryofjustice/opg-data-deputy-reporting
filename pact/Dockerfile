FROM python:3.11-slim

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_SESSION_TOKEN

RUN apt-get update && apt-get install -y curl wget
RUN curl -L -o /usr/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 \
&& chmod a+x /usr/bin/jq
RUN pip3 install awscli
COPY requirements.txt check_pact_deployable.py login_code_artifact.sh check_pact_deployable.sh ./
RUN chmod +x check_pact_deployable.sh && chmod +x login_code_artifact.sh
RUN ./login_code_artifact.sh -a 288342028542 -t pip
RUN pip3 install -r requirements.txt
RUN wget https://github.com/pact-foundation/pact-ruby-standalone/releases/download/v1.82.3/pact-1.82.3-linux-x86_64.tar.gz
RUN tar xzf pact-1.82.3-linux-x86_64.tar.gz
CMD [ "./check_pact_deployable.sh" ]