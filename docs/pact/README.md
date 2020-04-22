### Pact

#### What is it?

Pact as we use it, is made up of a consumer (in this case digideps),
a provider (data deputy reporting) and a pact broker.

The consumer creates a contract based on the data that it wishes to send
across and the format that the data should comply with. For example what
fields should appear in the body and how those fields should be validated.

It then tests this against it's own mock end point and creates a contract file
that includes the validation rules, an example request and an example response.

This contract is then uploaded to the pact broker which acts as a repository for the
consumer and provider pacts and as a source of truth for which versions have been verified
and against which other versions.

On the provider side, the consumer pact is run against the provider mock endpoint which should
directly replicate the real end point. If it does, a verification check can be made that updates
a matrix inside the pact broker to show which versions match.

#### Pact CI Workflow

Provider Side
- Run on commit
- Not on master branch

Verify current provider git_commit against latest consumer git_commit tagged with v<x>
Verify current provider git_commit against latest consumer git_commit tagged with v<x>_production

Canideploy with provider git_commit against latest consumer tagged with v<x>_production
If no rows found for consumer with tag v<x>_production
  Canideploy with provider git_commit against latest consumer tagged with v<x>

If true then allow build

Consumer side
- Run on commit
- Run against master branch of the provider side

Verify this commit against what is in master using GIT_SHA
tag provider with latest version tag (this may be different to what version is being passed from digideps)

CanIDeploy with consumer git_commit and latest provider tagged with v<x>_production (must get version from tags)

If true then send status update to github

Simplified diagram below:

![Alt text](pactdiagram.png?raw=true "PactDiagram")
