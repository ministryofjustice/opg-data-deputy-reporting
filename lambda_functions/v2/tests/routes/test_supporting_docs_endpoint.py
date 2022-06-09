import json

import pytest
import requests
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v2.tests.routes import cases_supporting_docs_endpoint


@pytest.mark.run(order=1)
@pytest.mark.usefixtures(
    "patched_s3_client",
    "patched_s3_file",
    "patched_get_secret",
    "patched_post",
    "patched_send_get_to_sirius",
    "patched_get_request_details_for_logs",
)
@cases_data(module=cases_supporting_docs_endpoint, has_tag="success")
def test_supporting_docs(server, case_data: CaseDataGetter):
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

        r = requests.post(
            f"{server.url}/clients/{test_case_ref}/reports/"
            f"{test_report_id}/supportingdocuments",
            headers=test_headers,
            data=json.dumps(test_data),
        )

        assert r.status_code == expected_response_status_code
        assert r.json() == expected_response_data


@pytest.mark.run(order=1)
@pytest.mark.usefixtures(
    "patched_s3_client",
    "patched_s3_file",
    "patched_get_secret",
    "patched_post_broken_sirius",
    "patched_send_get_to_sirius",
    "patched_get_request_details_for_logs",
)
@cases_data(module=cases_supporting_docs_endpoint, has_tag="error")
def test_supporting_docs_errors(server, case_data: CaseDataGetter):
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

        r = requests.post(
            f"{server.url}/clients/{test_case_ref}/reports/"
            f"{test_report_id}/supportingdocuments",
            headers=test_headers,
            data=json.dumps(test_data),
        )

        assert r.status_code == expected_response_status_code
        if r.status_code in [400]:
            assert r.json()["body"]["error"]["code"] == expected_response_data
