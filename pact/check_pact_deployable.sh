#!/usr/bin/env bash
set -e

echo "API version is: ${API_VERSION}"
python check_pact_deployable.py \
--provider_base_url="http://localhost:4343" \
--pact_broker_url="${PACT_BROKER_BASE_URL}" \
--broker_user_name="admin" \
--broker_secret_name="pactbroker_admin" \
--consumer_pacticipant="${PACT_CONSUMER}" \
--provider_pacticipant="${PACT_PROVIDER}" \
--api_version="${API_VERSION}" \
--git_commit_consumer="${GIT_COMMIT_CONSUMER}" \
--git_commit_provider="${GIT_COMMIT_PROVIDER}"