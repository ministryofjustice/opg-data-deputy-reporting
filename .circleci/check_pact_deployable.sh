export FULL_COMMIT_SHA=$(curl -u "${GITHUB_STATUS_CREDS}" \
-X GET https://"${GITHUB_DIGIDEPS_URL}"/commits/$CONSUMER_VER | jq -r .sha) >> /dev/null

./pact/bin/pact-broker can-i-deploy \
--broker-base-url https://$PACT_BROKER_BASE_URL \
--broker-username=$PACT_BROKER_HTTP_AUTH_USER \
--broker-password=$PACT_BROKER_HTTP_AUTH_PASS \
--pacticipant "Complete the deputy report" \
--version $CONSUMER_VER \
--pacticipant "OPG Data" \
--latest "production"

export CAN_DEPLOY=$?

echo "CAN_DEPLOY return code is: ${CAN_DEPLOY}"

if [ "${CAN_DEPLOY}" == "0" ]
then
printf "\n\nGithub Status Updated - Verified\n\n"
curl -X POST \
-H "Content-Type: application/json" \
-u "${GITHUB_STATUS_CREDS}" \
-d '{"state":"success","target_url":"https://'"${PACT_BROKER_BASE_URL}"'/","description":"Our build was verified!","context":"pactbroker"}' \
https://"${GITHUB_DIGIDEPS_URL}"/statuses/"${FULL_COMMIT_SHA}"
else
printf "\n\nGithub Status Updated - Failed\n\n"
curl -X POST \
-H "Content-Type: application/json" \
-u "${GITHUB_STATUS_CREDS}" \
-d '{"state":"failure","target_url":"https://'"${PACT_BROKER_BASE_URL}"'/","description":"Our build failed verification!","context":"pactbroker"}' \
https://"${GITHUB_DIGIDEPS_URL}"/statuses/"${FULL_COMMIT_SHA}"
fi
