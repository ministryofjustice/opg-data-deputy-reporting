#!/usr/bin/env bash
set -e
if [ "${CONSUMER_TRIGGERED}" == "false" ]
then
    #  Verify current provider git_commit against latest consumer git_commit tagged with v<x>
    ./pact/bin/pact-provider-verifier --provider-base-url=http://localhost:4343 \
    --custom-provider-header 'Authorization: asdf1234567890' \
    --pact-broker-base-url="https://${PACT_BROKER_BASE_URL}" \
    --provider="OPG Data" \
    --broker-username="${PACT_BROKER_HTTP_AUTH_USER}" \
    --broker-password="${PACT_BROKER_HTTP_AUTH_PASS}" -r \
    --consumer-version-tag="${PROVIDER_VERSION}" \
    --provider-version-tag="${PROVIDER_VERSION}" \
    --provider-app-version="${GIT_COMMIT_PROVIDER}" || echo "Error validating, didn't validate"

    # Verify current provider git_commit against latest consumer git_commit tagged with v<x>_production
    ./pact/bin/pact-provider-verifier --provider-base-url=http://localhost:4343 \
    --custom-provider-header 'Authorization: asdf1234567890' \
    --pact-broker-base-url="https://${PACT_BROKER_BASE_URL}" \
    --provider="OPG Data" \
    --broker-username="${PACT_BROKER_HTTP_AUTH_USER}" \
    --broker-password="${PACT_BROKER_HTTP_AUTH_PASS}" -r \
    --consumer-version-tag="${PROVIDER_VERSION}_production" \
    --provider-version-tag="${PROVIDER_VERSION}" \
    --provider-app-version="${GIT_COMMIT_PROVIDER}" || echo "Error validating, didn't validate"
elif [ "${CONSUMER_TRIGGERED}" == "true" ]
then
  printf "\n\nConsumer verification not done here. See check_pact_deployable.sh\n\n"
else
  echo "Error! Environment variable DIGIDEPS_TRIGGERED must be set to true or false"
  exit 1
fi
