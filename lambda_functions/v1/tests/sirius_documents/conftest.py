import json

import pytest
import requests

from lambda_functions.v1.functions.reports import reports as sirius_service_reports
from lambda_functions.v1.functions.supporting_docs import (
    supporting_docs as sirius_service_supporting_docs,
)

test_data = {
    "valid_clients": ["valid_client_id", "0319392T"],
    "invalid_clients": ["invalid_client_id"],
}


@pytest.fixture(autouse=True)
def sirius_request():
    return {
        "type": "Report - General",
        "caseRecNumber": "default_case_ref",
        "metadata": {
            "reporting_period_from": "2019-01-01",
            "reporting_period_to": "2019-12-31",
            "year": "2019",
            "date_submitted": "2020-01-03T09:30:00.001Z",
            "type": "HW",
        },
        "file": {
            "name": "default_file_name.pdf",
            "source": "string",
            "type": "application/pdf",
        },
    }


@pytest.fixture(autouse=True)
def mock_env_setup(monkeypatch):
    monkeypatch.setenv("BASE_URL", "http://localhost:8080")
    monkeypatch.setenv("SIRIUS_BASE_URL", "http://sirius_url.com")
    monkeypatch.setenv("SIRIUS_PUBLIC_API_URL", "api/public/v1/")
    monkeypatch.setenv("LOGGER_LEVEL", "DEBUG")
    monkeypatch.setenv("JWT_SECRET", "THIS_IS_MY_SECRET_KEY")
    monkeypatch.setenv("ENVIRONMENT", "development")


@pytest.fixture
def patched_requests(monkeypatch):
    def mock_post(*args, **kwargs):
        data = kwargs["data"]

        mock_response = requests.Response()

        try:
            if json.loads(data)["caseRecNumber"] in test_data["valid_clients"]:
                mock_response.status_code = 201
                mock_response._content = (
                    '{"uuid": '
                    '"531ca3b6-3f17-4ece-bdc5-7faf7f1f8427"}'.encode("UTF-8")
                )
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

    monkeypatch.setattr(sirius_service_reports, "get_secret", mock_secret)


@pytest.fixture
def patched_get_secret_supporting_docs(monkeypatch):
    def mock_secret(*args, **kwargs):
        return "this_is_a_secret_string"

    monkeypatch.setattr(sirius_service_supporting_docs, "get_secret", mock_secret)
