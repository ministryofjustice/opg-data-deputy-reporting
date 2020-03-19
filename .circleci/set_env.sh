#!/usr/bin/env bash
export SECRETSTRING=`aws sts assume-role \
--role-arn "arn:aws:iam::${ACCOUNT}:role/get-pact-secret-development" \
--role-session-name AWSCLI-Session | \
jq -r '.Credentials.SessionToken + \
" " + .Credentials.SecretAccessKey + \
" " + .Credentials.AccessKeyId'`

export AWS_ACCESS_KEY_ID=`echo $SECRETSTRING | awk -F' ' '{print $3}'`
export AWS_SECRET_ACCESS_KEY=`echo $SECRETSTRING | awk -F' ' '{print $2}'`
export AWS_SESSION_TOKEN=`echo $SECRETSTRING | awk -F' ' '{print $1}'`
# show which role is being assumed
# aws sts get-caller-identity | grep "arn:aws:sts"

export PACT_BROKER_PASS=`aws secretsmanager get-secret-value \
--secret-id pactbroker_admin \
--region eu-west-1 | jq -r '.SecretString'`

# set up machine user
# export GITHUB_STATUS=`aws secretsmanager get-secret-value \
# --secret-id github_machine_token \
# --region eu-west-1 | jq -r '.SecretString'`

PACT_BROKER_ADMIN="admin"
PACT_BASE_URL="dev-pact-broker.api.opg.service.justice.gov.uk"

echo "export GITHUB_STATUS_CREDS=${GITHUB_STATUS}"
echo "export PACT_BROKER_BASE_URL=${PACT_BASE_URL}"
echo "export PACT_BROKER_HTTP_AUTH_USER=${PACT_BROKER_ADMIN}"
echo "export PACT_BROKER_HTTP_AUTH_PASS=${PACT_BROKER_PASS}"

WORKSPACE=${WORKSPACE:-$CIRCLE_BRANCH}
WORKSPACE=${WORKSPACE//[^[:alnum:]]/}
WORKSPACE=${WORKSPACE,,}
WORKSPACE=${WORKSPACE:0:14}
echo "export TF_WORKSPACE=${WORKSPACE}"
TF_VAR_stage=`grep -A1 'info:' deputy-reporting-openapi.yml | grep 'version:' | head -1 | awk '{print $2}' | sed 's/\./_/g'`
echo "export TF_VAR_stage=${TF_VAR_stage}"
