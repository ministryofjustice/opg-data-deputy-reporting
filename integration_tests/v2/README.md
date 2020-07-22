# Integration tests

### Purpose

The integration test suites aren't part of the pipeline as they create real data on the sirius side
(against whatever branch you point them to). Their purpose is to give us confidence that all our real world
infrastructure is working as it should for all of our happy and unhappy paths.

They are to be run either locally against our mock or against real world infrastructure (not live!).

### Prerequisites

To set up for the integration tests you should check a few things first:

 - In `conftest.py`, check that the branch you are pointing to is correct.
 - In `conftest.py`, check that the `configs_to_test` is set to what you want to test against.
 - In `conftest.py`, take note of the case number you will be testing against.
 - Open sirius (in env you are testing against) and make sure the case exists. Create it if not.

 ### Run the tests
 create a virtualenv:

 - `virtualenv venv`
 - `source venv/bin/activate`

 `cd` into this folder and run `pip install -r ../../lambda_functions/v2/requirements/dev-requirements` or
 whatever requirements you need for your version.

 Run `aws-vault exec identity -- python -m pytest` and all integration tests will run against your setup.

 ### Gotchas

 Many of the tests need to be run in a single run as they use the output from previous tests to drive current tests.

 Make sure you are able to assume digideps dev role with your credentials or tests will not work.
