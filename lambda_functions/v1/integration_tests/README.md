# **'Integration' Tests**


These tests send a payload to a real url, be careful where you point things if you're going to run these.

These are not run as part of the regular unit tests. Use at your own risk

#### To Do

* Local mock Sirius needs fixing so this can be included in these tests
* AWS creds have to be pasted into `conftest.py` for now. Please don't commit these.
* Only happy path tests right now
* No checklist tests yet
* Uploaded records could be formatted nicer making it easier to reconcile with Sirius if required
