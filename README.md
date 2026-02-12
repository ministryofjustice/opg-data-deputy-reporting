# opg-data-deputy-reporting

[![CircleCI](https://circleci.com/gh/ministryofjustice/opg-data-deputy-reporting/tree/master.svg?style=svg)](https://circleci.com/gh/ministryofjustice/opg-data-deputy-reporting/tree/master)

Deputy reporting integration with OPG Data: Managed by opg-org-infra &amp; Terraform

### Path specific naming conventions.

Paths are product and environment specific and use delegated domains to create a hierarchy
to support this implementation.

The Rest APIs will be accessible externally in production from
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
make build
```

```
make up
```

The curl to the lambda that mimics what is sent by the API gateway is a bit of a funny format and url.
An example is below.

```
curl -XPOST "http://localhost:9009/2015-03-31/functions/function/invocations" -d '@./scripts/support/report_pdf_post.json' | jq
```

There will be some future work to better mimic the API Gateway fully locally.

### Unit tests

Unit tests can be run through the unit tests container and are also run in the pipeline.

```
make unit-tests
```

### Integration Tests

These tests send a payload to a real url, be careful where you point things if you're going to run these.

They run as part of the pipeline against a mock sirius endpoint that gets spun up and spun back down again
after the tests are finished.

Further instructions to follow for running against real environments.
