import json

import pytest
import requests
from pytest_cases import parametrize_with_cases

from lambda_functions.v2.tests.routes import (
    cases_checklist_post_endpoint,
    cases_checklist_put_endpoint,
)


@pytest.mark.run(order=1)
@pytest.mark.usefixtures(
    "patched_get_secret", "patched_post", "patched_get_request_details_for_logs"
)
@parametrize_with_cases(
    "test_data,test_headers,test_report_id,test_case_ref,expected_response_status_code,expected_response_data",
    cases=cases_checklist_post_endpoint
)
def test_checklist_post(
        server,
        test_data,
        test_headers,
        test_report_id,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
):

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
@pytest.mark.usefixtures(
    "patched_get_secret", "patched_post", "patched_get_request_details_for_logs"
)
@parametrize_with_cases(
    "test_data,test_headers,test_report_id,test_checklist_id,test_case_ref,expected_response_status_code,"
    "expected_response_data",
    cases=cases_checklist_put_endpoint
)
def test_checklist_put(
        server,
        test_data,
        test_headers,
        test_report_id,
        test_checklist_id,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
):

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
