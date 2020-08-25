# opg-data-deputy-reporting
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

The environment is deployed on a push to a branch and to raise a PR, you must
pass the branch destroy approval step. Please be aware that even if you decide to delete
your branch you should click on this step before doing so. This will stop us having orphaned
environments.

On merge of the PR the changes are applied into development and preproduction and after
a further approval, production.

### Authentication and local testing

Because the frontend is using IAM auth to access the endpoints, you must have temporary
credentials for one of the roles that is authorised to access the endpoint if you want to
test locally. You can use the scripts in docs/supportscripts folder with aws-vault to test the
endpoints locally. You can use getcreds.go script with aws-vault (aws-vault exec <your-profile> --
go run getcreds.go) and paste the outputs into appropriate section
of your GUI API testing tools (like postman) to test the endpoints that way.

### Unit tests

Unit tests can be run by creating a `virtual env` (see below for some instructions), installing the test requirements
and running `python -m pytest lambda_functions` from the root directory.

You may also need to update your `PYTHONPATH` env var to point to the root of the repo.

### 'Integration' Tests

These tests send a payload to a real url, be careful where you point things if you're going to run these.

These are not run as part of the regular unit tests. Use at your own risk

#### How to run

Pre-requirements:

1) Have aws-vault installed and set up

To run the integration tests in their entirety:

1) From root dir, jump in to a venv: `virtualenv venv`
2) Activate it: `source venv/bin/activate`
3) Install pip requirements: `pip install -r lambda_functions/v1/requirements/dev-requirements.txt`
4) Make sure $PYTHONPATH is set to root of directory.
5) Ensure the integration tests run on the desired branch environment by updating the URLs in `lambda_functions/(v1)/integration_tests/conftest.py`
6) `cd` into integrations test folder and run `aws-vault exec identity -- python -m pytest -n2 --dist=loadfile --html=report.html --self-contained-html`
7) Open `report.html` in a browser to see the results of the tests all laid out nicely

To run specific integration test(s), use Pytest Markers:

1) Add your new marker name to pytest.ini to avoid warnings, in the form `new_marker_name: description`
2) Add marker decorations to the test(s) you want to run:

```
@pytest.mark.new_marker_name
def test_my_lovely_test():
    ...
```

3)  Run like `aws-vault exec identity -- python -m pytest test_all_routes_happy_path.py -k "new_marker_name" -n2 -s --dist=loadfile --html=report.html --self-contained-html`
4) Open `report.html` in a browser to see the results of the tests all laid out nicely

#### Integration tests... still To Do

* Local mock Sirius needs fixing so this can be included in these tests
* Uploaded records could be formatted nicer making it easier to reconcile with Sirius if required

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
http://localhost:4343/v1/clients/1234567T/reports/33ea0382-cfc9-4776-9036-667eeb68fa4b/supportingdocuments
```
