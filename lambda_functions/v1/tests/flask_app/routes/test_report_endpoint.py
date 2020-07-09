import json

import pytest
import requests
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.tests.flask_app.routes import cases_reports_endpoint


@pytest.mark.run(order=1)
@pytest.mark.usefixtures("patched_get_secret", "patched_post")
@cases_data(module=cases_reports_endpoint, has_tag="success")
def test_reports(server, case_data: CaseDataGetter):
    (
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
    ) = case_data.get()

    with server.app_context():

        r = requests.post(
            f"{server.url}/clients/{test_case_ref}/reports",
            headers=test_headers,
            data=json.dumps(test_data),
        )

        assert r.json() == expected_response_data


@pytest.mark.run(order=1)
@pytest.mark.usefixtures("patched_get_secret", "patched_post_broken_sirius")
@cases_data(module=cases_reports_endpoint, has_tag="error")
def test_reports_errors(server, case_data: CaseDataGetter):
    (
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
    ) = case_data.get()

    with server.app_context():

        r = requests.post(
            f"{server.url}/clients/{test_case_ref}/reports",
            headers=test_headers,
            data=json.dumps(test_data),
        )

        if r.status_code in [400]:
            assert r.json()["body"]["error"]["code"] == expected_response_data
