import json

import pytest
import requests
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.tests.flask_app.routes import (
    cases_checklist_post_endpoint,
    cases_checklist_put_endpoint,
)


@pytest.mark.run(order=1)
@pytest.mark.usefixtures("patched_get_secret", "patched_submit_document_to_sirius")
@cases_data(module=cases_checklist_post_endpoint)
def test_checklist_post(server, case_data: CaseDataGetter):
    (
        test_data,
        test_headers,
        test_report_id,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
    ) = case_data.get()

    with server.app_context():

        print(f"test_case_ref: {test_case_ref}")
        print(f"test_report_id: {test_report_id}")
        print(f"test_data: {test_data}")
        print(f"server.url: {server.url}")

        r = requests.post(
            f"{server.url}/clients/{test_case_ref}/reports/"
            f"{test_report_id}/checklists",
            headers=test_headers,
            data=json.dumps(test_data),
        )

        assert r.status_code == expected_response_status_code
        assert r.json() == expected_response_data


@pytest.mark.run(order=1)
@pytest.mark.usefixtures("patched_get_secret", "patched_submit_document_to_sirius")
@cases_data(module=cases_checklist_put_endpoint)
def test_checklist_put(server, case_data: CaseDataGetter):
    (
        test_data,
        test_headers,
        test_report_id,
        test_checklist_id,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
    ) = case_data.get()

    with server.app_context():

        print(f"test_case_ref: {test_case_ref}")
        print(f"test_report_id: {test_report_id}")
        print(f"test_data: {test_data}")

        r = requests.put(
            f"{server.url}/clients/{test_case_ref}/reports/"
            f"{test_checklist_id}/checklists/{test_checklist_id}",
            headers=test_headers,
            data=json.dumps(test_data),
        )

        assert r.status_code == expected_response_status_code
        assert r.json() == expected_response_data
