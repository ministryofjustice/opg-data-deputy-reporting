# opg-data-deputy-reporting

[![CircleCI](https://circleci.com/gh/ministryofjustice/opg-data-deputy-reporting/tree/master.svg?style=svg)](https://circleci.com/gh/ministryofjustice/opg-data-deputy-reporting/tree/master)

Deputy reporting integration with OPG Data: Managed by opg-org-infra &amp; Terraform

### Path specific naming conventions

Paths are product and environment specific and use delegated domains to create a hierarchy
to support this implementation.

The Rest APIs will be be accessible externally in production from
deputy-reporting.api.opg.service.justice.gov.uk which is a
sub domain of opg.service.justice.gov.uk and this zone is created in the
management account.

We use further subdomains for deployment to preproduction (pre) and development (dev) and
further subdomains development for branch based deployment. For example, a uri to a
healthcheck endpoint created on PR1234 would like
PR1234.dev.api.deputy-reporting.api.opg.service.justice.gov.uk/v1/healthcheck.

New certs aren't created per branch as the sub branches use the wildcard cert for dev sub domain.

### Deployment of RestAPIs

The rest APIs deploy through a circleci job. The deployments are separate for each branch
and the uri for your branch will follow the pattern above.

The environment is deployed on raising a PR.

On merge of the PR the changes are applied into development and preproduction and after
a further approval, production.

### Destruction of environment

Environments are protected by default for the remainder of the current day until midnight the subsequent day.
They are then deleted by a job that runs that night. If you need environments to last longer than this then you can
update the TTL in for your branch in workspace protection table in dynamodb.

### Authentication and checking AWS endpoints from local machine

Because the frontend is using IAM auth to access the endpoints, you must have temporary
credentials for one of the roles that is authorised to access the endpoint if you want to
test locally. You can use the scripts in docs/supportscripts folder with aws-vault to test the
endpoints locally.

If you want to use a tool like postman that requires credentials, you can use getcreds.go script with
aws-vault (aws-vault exec <your-profile> -- go run getcreds.go) and paste the outputs into appropriate section
of your GUI API testing tool (postman for example)

### Manually testing the lambda image

As the lambda is built from an image, you can manually spin this up locally and test the payloads that API
gateway would send to it to check it responds as expected.

First bring up the lambda and the mock sirius containers as well as localstack which will be used for local S3.

```
docker-compose build mock-lambda mock-sirius localstack
```

```
docker-compose up -d mock-lambda
```

The curl to the lambda that mimics what is sent by the API gateway is a bit of a funny format and url.
An example is below.

```
curl -XPOST "http://localhost:9009/2015-03-31/functions/function/invocations" -d '@./docs/supportscripts/lambda_request.json' | jq
```

There will be some future work to mimic the API Gateway fully locally.

### Unit tests

Unit tests can be run through the unit tests container and are also run in the pipeline.

```
docker-compose up unit-tests
```

### Integration Tests

These tests send a payload to a real url, be careful where you point things if you're going to run these.

They run as part of the pipeline against a mock sirius endpoint that gets spun up and spun back down again
after the tests are finished.

Further instructions to follow for running against real environments.

### PACT

To run pact locally, the easiest way to interact with it is to use the client tools.

The best package to get started can be found here:

https://github.com/pact-foundation/pact-ruby-standalone/releases/latest

You can download the latest version to a directory, unzip it and run the individual tools
in the `/pact/bin` folder from the command line or put them in your PATH.
First you should put the contract in our local broker. The local broker is spun up as part
of the `docker-compose up -d` command and you can push in a contract manually from a json file
by using the below command (example json included in this repo):

```
curl -i -X PUT -d '@./pact/example/digideps-pact-v2.json' \
-H 'Content-Type: application/json' \
http://localhost:9292/pacts/provider/OPG%20Data/consumer/Complete%20the%20deputy%20report/version/x12345
```

You can then check it has uploaded by browsing to `localhost:9292`.

To tag the pact we can now run this. We will want to tag the consumer as
the verification command is best used with tags:

```
curl -i -X PUT -H 'Content-Type: application/json' \
http://localhost:9292/pacticipants/Complete%20the%20deputy%20report/versions/x12345/tags/v2
```

You can check it has worked here:

`http://localhost:9292/matrix/provider/OPG%20Data/consumer/Complete%20the%20deputy%20report`

You can verify the pact as follows (assuming your path to pact-provider-verifier is correct):

```
../pact/bin/pact-provider-verifier --provider-base-url=http://localhost:4343 \
--custom-provider-header 'Authorization: asdf1234567890' \
--pact-broker-base-url="http://localhost:9292" \
--provider="OPG Data" \
--consumer-version-tag=v2 \
--provider-version-tag=v2 \
--publish-verification-results \
--provider-app-version=z12345
```

To test with our full `check_pact_deployable.py` script that has all the version control embedded in it:

First you will want to pretend that `OPG Data` side has been tagged for production.

```
curl -i -X PUT -H 'Content-Type: application/json' http://localhost:9292/pacticipants/OPG%20Data/versions/z12345/tags/v2_production
```

You should do all of this in a virtual env (`virtualenv venv && source ./venv/bin/activate`)

You can then login to code artifact to pull the pact package (and logout again):

```
aws-vault exec sirius-dev -- aws codeartifact login \
--tool pip \
--repository opg-pip-shared-code-dev \
--domain opg-moj \
--domain-owner 288342028542 \
--region eu-west-1

pip3 install -r /pact/requirements.txt

pip config unset global.index-url
```

You can now run the script against your spun up environment:

```
aws-vault exec identity -- python3 check_pact_deployable.py \
--provider_base_url="http://localhost:4343" \
--pact_broker_url="http://localhost:9292" \
--broker_user_name="admin" \
--broker_secret_name="local" \
--consumer_pacticipant="Complete%20the%20deputy%20report" \
--provider_pacticipant="OPG%20Data" \
--api_version="v2" \
--git_commit_consumer="x12345" \
--git_commit_provider="z12345"
```

Further examples of posting adhoc payloads to the endpoint via curl can be seen below.
This may help in development of further integrations.

Post an example report to the endpoint

```
curl -X POST -d '@./mock_integration_rest_api/example_report.json' \
-H 'Authorization: asdf1234567890' \
-H 'Content-Type: application/json' \
http://localhost:4343/v2/clients/1234567T/reports
```

Post to an example supporting document to the endpoint

```
curl -X POST -d '@./mock_integration_rest_api/example_supporting_doc.json' \
-H 'Authorization: asdf1234567890' \
-H 'Content-Type: application/json' \
http://localhost:4343/v2/clients/1234567T/reports/33ea0382-cfc9-4776-9036-667eeb68fa4b/supportingdocuments
```
