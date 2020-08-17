#!/usr/bin/env bash
set -e
PACT_BROKER_ADMIN="admin"
PACT_BASE_URL="https://pact-broker.api.opg.service.justice.gov.uk"
PROVIDER="OPG%20Data"
CONSUMER="Complete%20the%20deputy%20report"
DIGIDEPS_URL="api.github.com/repos/ministryofjustice/opg-digideps"
ACCOUNT="997462338508"

WORKSPACE=${WORKSPACE:-$CIRCLE_BRANCH}
WORKSPACE=${WORKSPACE//[^[:alnum:]]/}
WORKSPACE=${WORKSPACE,,}
WORKSPACE=${WORKSPACE:0:14}
API_VERSION="v2"
GIT_COMMIT=${CIRCLE_SHA1:0:7}

echo "export GIT_COMMIT_PROVIDER=${GIT_COMMIT}"
echo "export TF_WORKSPACE=${WORKSPACE}"
echo "export API_VERSION=${API_VERSION}"
echo "export PACT_PROVIDER=${PROVIDER}"
echo "export PACT_CONSUMER=${CONSUMER}"
echo "export PACT_BROKER_BASE_URL=${PACT_BASE_URL}"
echo "export PACT_BROKER_HTTP_AUTH_USER=${PACT_BROKER_ADMIN}"
echo "export GITHUB_DIGIDEPS_URL=${DIGIDEPS_URL}"
