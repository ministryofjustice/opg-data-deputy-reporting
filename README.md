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
