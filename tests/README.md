> This document is WIP as there's not actually any tests yet, 
> so there's no need for instructions.


# Integration & Contract Testing

You can spin up all the supporting services locally using:

`docker-compose up`

in the root dir. This will create a mock Sirius Public API and a local Pact Broker


### Sirius Public API

Available on `http://0.0.0.0:4343/api/public/v1/ui/#` once running

### Pact Broker

Available on `http://0.0.0.0:9292` once running
