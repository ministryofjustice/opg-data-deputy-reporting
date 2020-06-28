# **'Integration' Tests**


These tests send a payload to a real url, be careful where you point things if you're going to run these.

These are not run as part of the regular unit tests. Use at your own risk

#### To Do

* Local mock Sirius needs fixing so this can be included in these tests
* AWS creds have to be pasted into `conftest.py` for now. Please don't commit these.
* Only happy path tests right now
* No checklist tests yet
* Uploaded records could be formatted nicer making it easier to reconcile with Sirius if required

#### How to run

Pre-requirements:

1) Have aws-vault installed and set up

To run the integration tests in their entirety:

1) From root dir, jump in to a venv: `virtualenv venv`
2) Activate it: `source venv/bin/activate`
3) Install pip requirements: `pip install -r lambda_functions/v1/requirements/dev-requirements.txt`
4) Make sure $PYTHONPATH is set to root of directory.
5) `cd` into integrations test folder and run `aws-vault exec identity -- python -m pytest`

