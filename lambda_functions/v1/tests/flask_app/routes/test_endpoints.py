import json
import logging

import requests
import pytest
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.tests.flask_app.routes import cases_test_endpoints


@pytest.mark.run(order=1)
@cases_data(module=cases_test_endpoints, has_tag="endpoint")
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

        assert r.status_code == expected_response_status_code
        assert r.json() == expected_response_data


@pytest.mark.run(order=1)
@cases_data(module=cases_test_endpoints, has_tag="environment")
def test_reports_environment(server, monkeypatch, caplog, case_data: CaseDataGetter):
    (
        env_var,
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_logger_message,
    ) = case_data.get()

    monkeypatch.delenv(env_var)

    with server.app_context():

        r = requests.post(
            f"{server.url}/clients/{test_case_ref}/reports",
            headers=test_headers,
            data=json.dumps(test_data),
        )

        assert r.status_code == expected_response_status_code

        with caplog.at_level(logging.ERROR):
            assert expected_logger_message in caplog.text
