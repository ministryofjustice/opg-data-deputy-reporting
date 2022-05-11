FROM python:3.7-slim

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_SESSION_TOKEN

COPY requirements.txt check_pact_deployable.py login_code_artifact.sh check_pact_deployable.sh .
RUN chmod +x check_pact_deployable.sh && chmod +x login_code_artifact.sh
RUN wget q -O /usr/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64
RUN pip3 install awscli
RUN ./login_code_artifact.sh -a 288342028542 -t pip
RUN pip3 install -r requirements.txt
CMD [ "check_pact_deployable.sh" ]