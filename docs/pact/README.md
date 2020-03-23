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

![Alt text](pactdiagram.png?raw=true "PactDiagram")
