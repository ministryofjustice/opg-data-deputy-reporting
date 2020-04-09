import json

import pytest
import requests


from lambda_functions.v1.functions.supporting_docs.app import supporting_docs
from lambda_functions.v1.functions.supporting_docs.app import sirius_service

test_data = {
    "valid_clients": ["valid_client_id", "0319392T", "12345678", "22814959"],
    "invalid_clients": ["invalid_client_id"],
}


@pytest.fixture(autouse=True)
def default_sirius_supporting_docs_request(
    default_request_case_ref, default_request_report_id
):
    return {
        "type": "Report",
        "caseRecNumber": default_request_case_ref,
        "metadata": {"submission_id": 231231, "report_id": default_request_report_id},
        "file": {
            "name": "Supporting_Document_111.pdf",
            "source": "string",
            "type": "application/pdf",
        },
    }


@pytest.fixture(autouse=True)
def default_supporting_doc_request_body(default_request_report_id):
    return {
        "supporting_document": {
            "data": {
                "type": "supportingdocuments",
                "id": default_request_report_id,
                "attributes": {"submission_id": 231231},
                "file": {
                    "name": "Supporting_Document_111.pdf",
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

    monkeypatch.setattr(sirius_service, "get_secret", mock_secret)


@pytest.fixture
def patched_validate_event(monkeypatch):
    def mock_invalid(*args, **kwargs):
        return False, ["file_name", "file_type"]

    monkeypatch.setattr(supporting_docs, "validate_event", mock_invalid)
