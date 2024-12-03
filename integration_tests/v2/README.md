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

 `cd` into this folder and run `pip install -r ../../lambda_functions/v2/requirements/unit-test-requirements.txt` or
 whatever requirements you need for your version.

 Run `aws-vault exec identity -- python -m pytest -n2 --dist=loadfile --html=report.html --self-contained-html` and
 all integration tests will run against your setup.

### Running the magic script

There is also a script that will check/create your specified caseref in Sirius for you, so you don't have to go do anything.
Before first run you must install the requirements (`pip3 install -r requirements.txt`) then the firefox geckodriver (for selenium):
```
wget https://github.com/mozilla/geckodriver/releases/download/v0.19.1/geckodriver-v0.19.1-linux64.tar.gz
tar xvfz geckodriver-v0.19.1-linux64.tar.gz
mv geckodriver ~/.local/bin
```

Then you can `cd integration_tests/v2` and run `python3 get_caseref.py` to check/create a given caseref.

Or, `cd integration_tests/v2` and run `sh run_integration_tests.sh` to run the check/create then run the tests for you.
This has one parameter, `-v`, which is optional. `sh run_integration_tests.sh -v "MoJ VPN` will connect to your VPN, sort out the caseref
and disconnect for you. If you do not supply your VPN name you'll have to press all those buttons by yourself.

Hint: if you keep the caseref in the `conftest.py` file the same as the one you use in the check/create script it will all just work.


 ### Gotchas

 Many of the tests need to be run in a single run as they use the output from previous tests to drive current tests.

 Make sure you are able to assume digideps dev role with your credentials or tests will not work.
