import json

import pytest
import requests
from pytest_cases import parametrize_with_cases

from lambda_functions.v2.tests.routes import cases_reports_endpoint


@pytest.mark.run(order=1)
@pytest.mark.usefixtures(
    "patched_get_secret",
    "patched_post",
    "patched_s3_client",
    "patched_s3_file",
    "patched_get_request_details_for_logs",
)
@parametrize_with_cases(
    "test_data,test_headers,test_case_ref,expected_response_status_code,expected_response_data",
    cases=cases_reports_endpoint, has_tag="success"
)
def test_reports(
        server,
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_response_data
):
    with server.app_context():
        r = requests.post(
            f"{server.url}/clients/{test_case_ref}/reports",
            headers=test_headers,
            data=json.dumps(test_data),
        )
        print(f"r.json(): {r.json()}")
        assert r.status_code == expected_response_status_code
        assert r.json() == expected_response_data


@pytest.mark.run(order=1)
@pytest.mark.usefixtures(
    "patched_get_secret",
    "patched_post_broken_sirius",
    "patched_s3_client",
    "patched_s3_file",
    "patched_get_request_details_for_logs",
)
@parametrize_with_cases(
    "test_data,test_headers,test_case_ref,expected_response_status_code,expected_response_data",
    cases=cases_reports_endpoint, has_tag="error"
)
def test_reports_errors(
        server,
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
):
    with server.app_context():
        r = requests.post(
            f"{server.url}/clients/{test_case_ref}/reports",
            headers=test_headers,
            data=json.dumps(test_data),
        )

        assert r.status_code == expected_response_status_code
        if r.status_code in [400]:
            assert r.json()["error"]["code"] == expected_response_data


@pytest.mark.run(order=1)
@pytest.mark.usefixtures(
    "patched_get_secret",
    "patched_post_broken_sirius",
    "patched_s3_client",
    "patched_s3_file",
    "patched_get_request_details_for_logs",
)
@parametrize_with_cases(
    "env_var,test_data,test_headers,test_case_ref,expected_response_status_code,expected_logger_message",
    cases=cases_reports_endpoint,
    has_tag="environment"
)
def test_reports_environment(
        server,
        monkeypatch,
        env_var,
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_logger_message
):

    monkeypatch.delenv(env_var)

    with server.app_context():
        r = requests.post(
            f"{server.url}/clients/{test_case_ref}/reports",
            headers=test_headers,
            data=json.dumps(test_data),
        )

        assert r.status_code == expected_response_status_code
