#!/usr/bin/env bash
set -e
PACT_BROKER_ADMIN="admin"
PACT_BASE_URL="pact-broker.api.opg.service.justice.gov.uk"
PROVIDER="OPG%20Data"
CONSUMER="Complete%20the%20deputy%20report"
DIGIDEPS_URL="api.github.com/repos/ministryofjustice/opg-digideps"
ACCOUNT="997462338508"

export SECRETSTRING=$(aws sts assume-role \
--role-arn "arn:aws:iam::${ACCOUNT}:role/get-pact-secret-production" \
--role-session-name AWSCLI-Session | \
jq -r '.Credentials.SessionToken + " " + .Credentials.SecretAccessKey + " " + .Credentials.AccessKeyId')

#local export so they only exist in this stage
export AWS_ACCESS_KEY_ID=$(echo "${SECRETSTRING}" | awk -F' ' '{print $3}')
export AWS_SECRET_ACCESS_KEY=$(echo "${SECRETSTRING}" | awk -F' ' '{print $2}')
export AWS_SESSION_TOKEN=$(echo "${SECRETSTRING}" | awk -F' ' '{print $1}')

export PACT_BROKER_PASS=$(aws secretsmanager get-secret-value \
--secret-id pactbroker_admin \
--region eu-west-1 | jq -r '.SecretString')

export GITHUB_CREDS=$(aws secretsmanager get-secret-value \
--secret-id integrations_github_credentials \
--region eu-west-1 | jq -r '.SecretString')

WORKSPACE=${WORKSPACE:-$CIRCLE_BRANCH}
WORKSPACE=${WORKSPACE//[^[:alnum:]]/}
WORKSPACE=${WORKSPACE,,}
WORKSPACE=${WORKSPACE:0:14}
PROVIDER_VER=$(ls -d lambda_functions/*/ | awk -F'/' '{print $2}' | sort -r | head -n1)

echo "export TF_WORKSPACE=${WORKSPACE}"
echo "export PROVIDER_VERSION=${PROVIDER_VER}"
echo "export PACT_PROVIDER=${PROVIDER}"
echo "export PACT_CONSUMER=${CONSUMER}"
echo "export GITHUB_STATUS_CREDS=${GITHUB_CREDS}"
echo "export PACT_BROKER_BASE_URL=${PACT_BASE_URL}"
echo "export PACT_BROKER_HTTP_AUTH_USER=${PACT_BROKER_ADMIN}"
echo "export PACT_BROKER_HTTP_AUTH_PASS=${PACT_BROKER_PASS}"
echo "export GITHUB_DIGIDEPS_URL=${DIGIDEPS_URL}"
