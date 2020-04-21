#!/usr/bin/env bash
set -e
if [ "${CONSUMER_TRIGGERED}" == "false" ]
then

    # Canideploy with provider git_commit against latest consumer tagged with v<x>_production
    CANIDEPLOY_RESPONSE=$(./pact/bin/pact-broker can-i-deploy \
    --broker-base-url="https://${PACT_BROKER_BASE_URL}" \
    --broker-username="${PACT_BROKER_HTTP_AUTH_USER}" \
    --broker-password="${PACT_BROKER_HTTP_AUTH_PASS}" \
    --pacticipant="Complete the deputy report" \
    --latest "${PROVIDER_VERSION}_production" \
    --pacticipant "OPG Data" \
    --version "${GIT_COMMIT_PROVIDER}" \
    | tail -1)

    # If the prod version doesn't exist then it's a breaking change or a new version
    # we are allowed to try the dev version
    if [ "$(echo "${CANIDEPLOY_RESPONSE}" \
        | grep -c "No version with tag ${PROVIDER_VERSION}_production exists for Complete the deputy report")" -eq 1 ]
    then
        # Canideploy with provider git_commit against latest consumer tagged with v<x>
        CANIDEPLOY_RESPONSE=$(./pact/bin/pact-broker can-i-deploy \
        --broker-base-url="https://${PACT_BROKER_BASE_URL}" \
        --broker-username="${PACT_BROKER_HTTP_AUTH_USER}" \
        --broker-password="${PACT_BROKER_HTTP_AUTH_PASS}" \
        --pacticipant="Complete the deputy report" \
        --latest "${PROVIDER_VERSION}_production" \
        --pacticipant "OPG Data" \
        --version "${GIT_COMMIT_PROVIDER}" \
        | tail -1)
    fi

    if [ "$(echo "${CANIDEPLOY_RESPONSE}" \
        | grep -c "No version with tag ${PROVIDER_VERSION} exists for Complete the deputy report")" -eq 1 ]
    then
        printf "\n\nProvider Side 'Can I Deploy' Failed! No matching consumer pact!\n\n"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY=false
    elif [ "$(echo "${CANIDEPLOY_RESPONSE}" | grep -c "failed")" -ne 0 ]
    then
        printf "\n\nProvider Side 'Can I Deploy' Failed!\n\n"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY=false
    elif [ "$(echo "${CANIDEPLOY_RESPONSE}" | grep -c "successful")" -ne 0 ]
    then
        printf "\n\nProvider Side 'Can I Deploy' Successful\n\n"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY="true"
    fi

    if [ ! "${CAN_I_DEPLOY}" ]
    then
        printf "\n\nFailing the build\n\n"
        exit
    fi

elif [ "${CONSUMER_TRIGGERED}" == "true" ]
then

    # Get the API version from the tag associated with consumer commit
    CONSUMER_API_VERSION=$(curl -u "${PACT_BROKER_HTTP_AUTH_USER}":"${PACT_BROKER_HTTP_AUTH_PASS}" \
    -X GET https://"${PACT_BROKER_BASE_URL}"/pacticipants/"${PACT_CONSUMER}"/versions/"${GIT_COMMIT_CONSUMER}" \
    | jq ._embedded.tags[] | jq .name | sed 's/"//g' | grep '^v[1-9]\+$' | sort -r | head -n1)
    printf "\n\nThe consumer version we are testing is %b\n\n" "${CONSUMER_API_VERSION}"

    # Get the full commit sha for later use
    export CONSUMER_FULL_COMMIT_SHA=$(curl -u "${GITHUB_STATUS_CREDS}" \
    -X GET https://"${GITHUB_DIGIDEPS_URL}"/commits/"${GIT_COMMIT_CONSUMER}" | jq -r .sha) >> /dev/null

    # CanIDeploy with consumer git_commit and latest provider tagged with v<x>_production (must get version from tags)
    CANIDEPLOY_RESPONSE=$(./pact/bin/pact-broker can-i-deploy \
    --broker-base-url "https://${PACT_BROKER_BASE_URL}" \
    --broker-username="${PACT_BROKER_HTTP_AUTH_USER}" \
    --broker-password="${PACT_BROKER_HTTP_AUTH_PASS}" \
    --pacticipant "Complete the deputy report" \
    --version "${GIT_COMMIT_CONSUMER}" \
    --pacticipant "OPG Data" \
    --latest "${CONSUMER_API_VERSION}_production" \
    | tail -1)

    if [ "$(echo "${CANIDEPLOY_RESPONSE}" | grep -c "There is no verified pact")" -eq 1 ]
    then
        # New Pact has not been verified before. We must verify it!
        # Verify this commit against what is in master using this providers GIT_SHA
        # Tag provider with latest version tag (this may be different to what version is being passed from digideps)
        # This is intended as we only want to allow changes that will work against the 'live' provider
        # There is an issue that what we're comparing against may be in master but not prod but it's a fringe case
        ./pact/bin/pact-provider-verifier --provider-base-url=http://localhost:4343 \
        --custom-provider-header 'Authorization: asdf1234567890' \
        --pact-broker-base-url="https://${PACT_BROKER_BASE_URL}" \
        --provider="OPG Data" \
        --broker-username="${PACT_BROKER_HTTP_AUTH_USER}" \
        --broker-password="${PACT_BROKER_HTTP_AUTH_PASS}" -r \
        --consumer-version-tag="${PROVIDER_VERSION}" \
        --provider-app-version="${GIT_COMMIT_PROVIDER}" || echo "Error validating, didn't validate"
        # Rerun can I deploy
        CANIDEPLOY_RESPONSE=$(./pact/bin/pact-broker can-i-deploy \
        --broker-base-url "https://${PACT_BROKER_BASE_URL}" \
        --broker-username="${PACT_BROKER_HTTP_AUTH_USER}" \
        --broker-password="${PACT_BROKER_HTTP_AUTH_PASS}" \
        --pacticipant "Complete the deputy report" \
        --version "${GIT_COMMIT_CONSUMER}" \
        --pacticipant "OPG Data" \
        --latest "${CONSUMER_API_VERSION}_production" \
        | tail -1)
    fi

    if [ "$(echo "${CANIDEPLOY_RESPONSE}" \
        | grep -c "No version with tag ${CONSUMER_API_VERSION} exists for OPG Data")" -eq 1 ]
    then
        printf "\n\nConsumer Side 'Can I Deploy' Failed! No matching consumer pact!\n\n"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY=false
    elif [ "$(echo "${CANIDEPLOY_RESPONSE}" | grep -c "failed")" -ne 0 ]
    then
        printf "\n\nConsumer Side 'Can I Deploy' Failed!\n\n"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY=false
    elif [ "$(echo "${CANIDEPLOY_RESPONSE}" | grep -c "successful")" -ne 0 ]
    then
        printf "\n\nConsumer Side 'Can I Deploy' Successful\n\n"
        echo "${CANIDEPLOY_RESPONSE}"
        export CAN_I_DEPLOY=true
    fi
    # Send status update to digideps
    if [ "${CAN_I_DEPLOY}" ]
    then
        printf "\n\nGithub Status Updated - Verification Successful\n\n"
        curl -X POST \
        -H "Content-Type: application/json" \
        -u "${GITHUB_STATUS_CREDS}" \
        -d '{"state":"success","target_url":"https://'"${PACT_BROKER_BASE_URL}"'/","description":"Our build was verified!","context":"pactbroker"}' \
        https://"${GITHUB_DIGIDEPS_URL}"/statuses/"${CONSUMER_FULL_COMMIT_SHA}"
    else
        printf "\n\nGithub Status Updated - Verification Failed\n\n"
        curl -X POST \
        -H "Content-Type: application/json" \
        -u "${GITHUB_STATUS_CREDS}" \
        -d '{"state":"failure","target_url":"https://'"${PACT_BROKER_BASE_URL}"'/","description":"Our build failed verification!","context":"pactbroker"}' \
        https://"${GITHUB_DIGIDEPS_URL}"/statuses/"${CONSUMER_FULL_COMMIT_SHA}"
    fi
else
    echo "Environment variable, CONSUMER_TRIGGERED not set"
    exit 1
fi
