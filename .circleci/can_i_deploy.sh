./pact/bin/pact-broker can-i-deploy \
--broker-base-url https://$PACT_BROKER_BASE_URL \
--broker-username=$PACT_BROKER_HTTP_AUTH_USER \
--broker-password=$PACT_BROKER_HTTP_AUTH_PASS \
--pacticipant "Complete the deputy report" \
--version $CONSUMER_VER \
--pacticipant "OPG Data" \
--latest "development"

export CAN_DEPLOY=`echo $?`
echo "CAN_DEPLOY?: ${CAN_DEPLOY}"
