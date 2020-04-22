from lambda_functions.v1.functions.healthcheck import healthcheck
import pytest
import requests

from lambda_functions.v1.tests.helpers.use_test_data import is_valid_schema


@pytest.fixture(autouse=True)
def mock_env_setup(monkeypatch):
    monkeypatch.setenv("SIRIUS_BASE_URL", "http://localhost:8080")
    monkeypatch.setenv("LOGGER_LEVEL", "DEBUG")


@pytest.fixture
def mock_service_status(monkeypatch):
    class MockResponse(object):
        def __init__(self):
            self.status_code = 200
            self.url = "http://fake_sirius/api/health-check/service-status"
            self.headers = {"myheader": "this is some header information"}
            self.text = {
                "ok": "true",
                "membrane": {"ok": "true", "status-code": 200},
                "api": {"ok": "true", "status-code": 200},
                "ddc-queue": {
                    "ok": "true",
                    "queue-type": "sqs",
                    "attributes": {
                        "VisibilityTimeout": "30",
                        "DelaySeconds": "0",
                        "ReceiveMessageWaitTimeSeconds": "0",
                        "ApproximateNumberOfMessages": "0",
                        "ApproximateNumberOfMessagesNotVisible": "0",
                        "ApproximateNumberOfMessagesDelayed": "0",
                        "CreatedTimestamp": "1581527140",
                        "LastModifiedTimestamp": "1581527140",
                        "QueueArn": "arn:aws:sqs:eu-west-1:000000000000:ddc.fifo",
                        "ContentBasedDeduplication": "true",
                        "FifoQueue": "true",
                    },
                },
            }

    def mock_get(url, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)


def test_get_response_success(mock_service_status):

    response = healthcheck.lambda_handler(event=None, context=None)
    is_valid_schema(response, "standard_lambda_response_schema.json")
    assert response["statusCode"] == 200
    assert len(response["body"]) == 4
