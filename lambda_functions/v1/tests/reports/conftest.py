import json

import pytest
import requests

from lambda_functions.v1.functions.reports.app import reports
from lambda_functions.v1.functions.reports.app import sirius_service

test_data = {
    "valid_clients": ["valid_client_id", "0319392T", "12345678", "22814959"],
    "invalid_clients": ["invalid_client_id"],
}


@pytest.fixture(autouse=True)
def default_sirius_reports_request(default_request_case_ref):
    return {
        "type": "Report - General",
        "caseRecNumber": default_request_case_ref,
        "metadata": {
            "submission_id": 12345,
            "reporting_period_from": "2019-01-01",
            "reporting_period_to": "2019-12-31",
            "year": 2019,
            "date_submitted": "2020-01-03T09:30:00.001Z",
            "type": "PF",
        },
        "file": {
            "name": "Report_1234567T_2018_2019_11111.pdf",
            "source": "string",
            "type": "application/pdf",
        },
    }


@pytest.fixture(autouse=True)
def default_report_request_body():
    return {
        "report": {
            "data": {
                "type": "reports",
                "attributes": {
                    "submission_id": 12345,
                    "reporting_period_from": "2019-01-01",
                    "reporting_period_to": "2019-12-31",
                    "year": 2019,
                    "date_submitted": "2020-01-03T09:30:00.001Z",
                    "type": "PF",
                },
                "file": {
                    "name": "Report_1234567T_2018_2019_11111.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }


@pytest.fixture(autouse=True)
def default_request_case_ref():
    return "12345678"


@pytest.fixture(autouse=True)
def default_request_report_id():
    return "df6ff8dd-01a3-4f02-833b-01655f9b4c9e"


@pytest.fixture(autouse=True)
def mock_env_setup(monkeypatch):
    monkeypatch.setenv("BASE_URL", "http://localhost:8080")
    monkeypatch.setenv("SIRIUS_BASE_URL", "http://sirius_url.com")
    monkeypatch.setenv("SIRIUS_PUBLIC_API_URL", "api/public/v1/")
    monkeypatch.setenv("LOGGER_LEVEL", "DEBUG")
    monkeypatch.setenv("JWT_SECRET", "THIS_IS_MY_SECRET_KEY")
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("SESSION_DATA", "publicapi@opgtest.com")
    monkeypatch.setenv("API_VERSION", "v1")


sirius_report_response = json.dumps(
    {
        "type": "Report",
        "filename": "3c1baa57f3cfa_Report_25558511_2018_2019_12345.pdf",
        "mimeType": "application/pdf",
        "metadata": {
            "reporting_period_from": "2019-01-01",
            "reporting_period_to": "2019-12-31",
            "year": 2019,
            "date_submitted": "2020-01-03T09:30:00.001Z",
            "type": "HW",
            "submission_id": 12345,
        },
        "uuid": "8ffdddb1-f19b-4c46-b4d1-9388ade95a68",
    }
)


@pytest.fixture
def patched_requests(monkeypatch):
    def mock_post(*args, **kwargs):
        data = kwargs["data"]

        mock_response = requests.Response()

        try:
            if json.loads(data)["caseRecNumber"] in test_data["valid_clients"]:
                mock_response.status_code = 201
                mock_response._content = sirius_report_response.encode("UTF-8")
            elif json.loads(data)["caseRecNumber"] is None:
                mock_response.status_code = 500
                mock_response.json = None
            else:
                mock_response.status_code = 400
                mock_response.json = None
        except KeyError:
            mock_response.status_code = 500
            mock_response.json = None

        return mock_response

    monkeypatch.setattr(requests, "post", mock_post)


@pytest.fixture
def patched_get_secret(monkeypatch):
    def mock_secret(*args, **kwargs):
        return "this_is_a_secret_string"

    monkeypatch.setattr(sirius_service, "get_secret", mock_secret)


@pytest.fixture
def patched_validate_event_fail(monkeypatch):
    def mock_invalid(*args, **kwargs):
        return False, ["file_name", "file_type"]

    monkeypatch.setattr(reports, "validate_event", mock_invalid)


@pytest.fixture
def patched_validate_event_success(monkeypatch):
    def mock_valid(*args, **kwargs):
        return True, []

    monkeypatch.setattr(reports, "validate_event", mock_valid)
