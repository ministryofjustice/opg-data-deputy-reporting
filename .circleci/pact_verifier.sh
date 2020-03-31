pact-verifier --provider-base-url=http://localhost:4343/1.0 \
--pact-url=https://"${PACT_BROKER_BASE_URL}"/pacts/provider/"${PACT_PROVIDER}"/consumer/"${PACT_CONSUMER}"/version/"${CONSUMER_VER}" \
--pact-broker-username="${PACT_BROKER_HTTP_AUTH_USER}" \
--pact-broker-password="${PACT_BROKER_HTTP_AUTH_PASS}" -r \
--provider-app-version="${PROVIDER_VERSION}" && echo "export FAIL_BUILD=false" >> "${BASH_ENV}" \
|| printf "\n\nPact Verification of %s Failed\n\n", "${CONSUMER_VER}" && echo "export FAIL_BUILD=true" >> "${BASH_ENV}"
