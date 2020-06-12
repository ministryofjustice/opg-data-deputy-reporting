# opg-data-deputy-reporting
Deputy reporting integration with OPG Data: Managed by opg-org-infra &amp; Terraform

#### Path specific naming conventions

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

#### Deployment of RestAPIs

The rest APIs deploy through a circleci job. The deployments are separate for each branch
and the uri for your branch will follow the pattern above.

The environment is deployed on a push to a branch and to raise a PR, you must
pass the branch destroy approval step. Please be aware that even if you decide to delete
your branch you should click on this step before doing so. This will stop us having orphaned
environments.

On merge of the PR the changes are applied into development and preproduction and after
a further approval, production.

#### Authentication and local testing

Because the frontend is using IAM auth to access the endpoints, you must have temporary
credentials for one of the roles that is authorised to access the endpoint if you want to
test locally. You can use the scripts in docs/supportscripts folder with aws-vault to test the
endpoints locally. You can use getcreds.go script with aws-vault (aws-vault exec <your-profile> --
go run getcreds.go) and paste the outputs into appropriate section
of your GUI API testing tools (like postman) to test the endpoints that way.

#### PACT

To run pact locally, the easiest way to interact with it is to use the client tools.

The best package to get started can be found here:

https://github.com/pact-foundation/pact-ruby-standalone/releases/latest

You can download the latest version to a directory, unzip it and run the individual tools
in the `/pact/bin` folder from the command line or put them in your PATH.
First you should put the contract in our local broker. The local broker is spun up as part
of the `docker-compose up -d` command and you can push in a contract manually from a json file
by using the below command (example json included in this repo):

```
curl -i -X PUT -d '@./mock_integration_rest_api/example_pact_contract.json' \
-H 'Content-Type: application/json' \
http://localhost:9292/pacts/provider/OPG%20Data/consumer/Complete%20the%20deputy%20report/version/x12345
```

You can then check it has uploaded by browsing to `localhost:9292`.

To tag the pact we can now run this. We will want to tag the consumer as
the verification command is best used with tags:

```
curl -i -X PUT -H 'Content-Type: application/json' \
http://localhost:9292/pacticipants/Complete%20the%20deputy%20report/versions/x12345/tags/v1
```

You can check it has worked here:

`http://localhost:9292/matrix/provider/OPG%20Data/consumer/Complete%20the%20deputy%20report`

You can verify the pact as follows (assuming your path to pact-provider-verifier is correct):

```
../pact/bin/pact-provider-verifier --provider-base-url=http://localhost:4343 \
--custom-provider-header 'Authorization: asdf1234567890' \
--pact-broker-base-url="http://localhost:9292" \
--provider="OPG Data" \
--consumer-version-tag=v1 \
--provider-version-tag=v1 \
--publish-verification-results \
--provider-app-version=1.2.3
```

Further examples of posting adhoc payloads to the endpoint via curl can be seen below.
This may help in development of further integrations.

Post an example report to the endpoint

```
curl -X POST -d '@./mock_integration_rest_api/example_report.json' \
-H 'Authorization: asdf1234567890' \
-H 'Content-Type: application/json' \
http://localhost:4343/v1/clients/1234567T/reports
```

Post to an example supporting document to the endpoint

```
curl -X POST -d '@./mock_integration_rest_api/example_supporting_doc.json' \
-H 'Authorization: asdf1234567890' \
-H 'Content-Type: application/json' \
http://localhost:4343/v1/clients/1234567T/reports/33ea0382-cfc9-4776-9036-667eeb68fa4b/supportingdocuments
```
