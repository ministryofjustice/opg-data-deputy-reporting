import json

import pytest

from lambda_functions.sirius_documents.post_report_to_sirius import (
    get_data_from_event,
    lambda_handler,
)
from tests.helpers.assertions import assert_valid_schema, is_valid_uuid

test_event = {
    "resource": "/clients/{caseref}/reports",
    "path": "clients/0319392T/reports",
    "httpMethod": "POST",
    "headers": None,
    "multiValueHeaders": None,
    "queryStringParameters": None,
    "multiValueQueryStringParameters": None,
    "pathParameters": {"caseref": "0319392T"},
    "stageVariables": None,
    "requestContext": {
        "resourceId": "emv1ml",
        "resourcePath": "/clients/{caseref}/reports",
        "httpMethod": "POST",
        "extendedRequestId": "Izj7oH3XLPEFj2g=",
        "requestTime": "03/Mar/2020:08:48:35 +0000",
        "path": "/reports/{id}",
        "accountId": "777546893854",
        "protocol": "HTTP/1.1",
        "stage": "test-invoke-stage",
        "domainPrefix": "testPrefix",
        "requestTimeEpoch": 1583225315903,
        "requestId": "76268751-c9cf-4d3f-a20d-9b4357fc0449",
    },
    "body": '{"caseRef": "0319392T", "direction": "DIRECTION_INCOMING", '
    '"documentSubType": "Report - General", "documentType": "Report - General",'
    ' "file": {"fileName": "Report_1234567T_2018_2019_11111.pdf", "mimeType": '
    '"application/pdf", "source": "string"}, "metaData": {}}',
    "isBase64Encoded": True,
}


@pytest.fixture(autouse=True)
def mock_env_setup(monkeypatch):
    monkeypatch.setenv("BASE_URL", "http://localhost:8080")
    monkeypatch.setenv("LOGGER_LEVEL", "DEBUG")


def test_get_data_from_event(event=test_event):
    result = get_data_from_event(event)
    assert_valid_schema(result, "sirius_documents_payload.json")


def test_lambda_handler(event=test_event, context=None):
    result = lambda_handler(event, context)

    result_body = json.loads(result)["body"]

    assert_valid_schema(result, "lambda_response.json")
    assert "uuid" in result_body
    assert is_valid_uuid(result_body["uuid"])
