import json

import pytest
import requests

from lambda_functions.reports.reports import (
    submit_document_to_sirius,
    transform_event_to_sirius_request,
    lambda_handler,
)
from tests.helpers.use_test_data import is_valid_schema, load_data

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


@pytest.fixture
def patched_requests(monkeypatch):
    def mock_post(*args, **kwargs):
        data = kwargs["data"]

        mock_response = requests.Response()

        try:
            if data["caseRecNumber"] in test_data["valid_clients"]:
                mock_response.status_code = 201
                mock_response.json = json.dumps(
                    {"uuid": "531ca3b6-3f17-4ece-bdc5-7faf7f1f8427"}
                )
            else:
                mock_response.status_code = 400
                mock_response.json = None
        except KeyError:
            mock_response.status_code = 500
            mock_response.json = None

        return mock_response

    monkeypatch.setattr(requests, "post", mock_post)


@pytest.mark.parametrize(
    "case_ref, expected_result",
    [
        (
            "valid_client_id",
            {
                "status_code": 201,
                "body": json.dumps({"uuid": "531ca3b6-3f17-4ece-bdc5-7faf7f1f8427"}),
            },
        ),
        ("invalid_client_id", {"status_code": 400, "body": "Invalid client id"}),
    ],
)
def test_submit_document_to_sirius(
    patched_requests, case_ref, expected_result, sirius_request
):
    headers = {"Content-Type": "application/json"}
    body = sirius_request
    body["caseRecNumber"] = case_ref

    response = submit_document_to_sirius(data=body, headers=headers)

    assert response["statusCode"] == expected_result["status_code"]
    assert response["body"] == expected_result["body"]
    assert is_valid_schema(response, "lambda_response.json")


def test_sirius_does_not_exist(monkeypatch, sirius_request):
    monkeypatch.setenv("SIRIUS_BASE_URL", "http://this_url_does_not_exist/")
    headers = {"Content-Type": "application/json"}
    body = sirius_request

    response = submit_document_to_sirius(data=body, headers=headers)

    assert response["statusCode"] == 404


def test_transform_event_to_sirius_request():
    event = load_data("lambda_event.json", as_json=False)

    payload = transform_event_to_sirius_request(event)

    assert is_valid_schema(payload, "sirius_documents_payload.json")


def test_lambda_handler(patched_requests):
    event = load_data("lambda_event.json", as_json=False)
    context = None

    result = lambda_handler(event=event, context=context)

    assert is_valid_schema(result, "lambda_response.json")
