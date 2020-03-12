import json

import pytest
import requests

from lambda_functions.sirius_documents.post_report_to_sirius import (
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
def mock_env_setup(monkeypatch):
    monkeypatch.setenv("BASE_URL", "http://localhost:8080")
    monkeypatch.setenv("SIRIUS_PUBLIC_API_URL", "http://sirius_url.com/api/public/v1/")
    monkeypatch.setenv("LOGGER_LEVEL", "DEBUG")


@pytest.fixture
def patched_requests(monkeypatch):
    def mock_post(*args, **kwargs):
        data = kwargs["data"]

        mock_response = requests.Response()

        # try:
        if data["caseRef"] in test_data["valid_clients"]:
            mock_response.status_code = 201
            mock_response.json = json.dumps(
                {"uuid": "531ca3b6-3f17-4ece-bdc5-7faf7f1f8427"}
            )
        else:
            mock_response.status_code = 400
            mock_response.json = None
        # except KeyError:
        #     mock_response.status_code = 500
        #     mock_response.json = None

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
def test_submit_document_to_sirius(patched_requests, case_ref, expected_result):
    headers = {"Content-Type": "application/json"}
    body = {
        "caseRef": case_ref,
        "direction": "DIRECTION_INCOMING",
        "documentSubType": "Report - General",
        "documentType": "Report - General",
        "file": {
            "fileName": "Report_1234567T_2018_2019_11111.pdf",
            "mimeType": "application/pdf",
            "source": "string",
        },
        "metaData": {},
    }

    response = submit_document_to_sirius(data=body, headers=headers)

    assert response["statusCode"] == expected_result["status_code"]
    assert response["body"] == expected_result["body"]


def test_transform_event_to_sirius_request():

    event = load_data("lambda_event.json", as_json=False)

    payload = transform_event_to_sirius_request(event)

    assert is_valid_schema(payload, "sirius_documents_payload.json")


def test_lambda_handler(patched_requests):
    event = load_data("lambda_event.json", as_json=False)
    context = None

    result = lambda_handler(event=event, context=context)

    print(result)

    assert is_valid_schema(result, "lambda_response.json")
