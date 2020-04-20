import json

import pytest
import requests

from lambda_functions.v1.functions.supporting_docs.app import sirius_service
from lambda_functions.v1.functions.supporting_docs.app import supporting_docs

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


sirius_sup_docs_response = json.dumps(
    {
        "type": "Report - General",
        "filename": "b11a291e6dae6_supportingDoc123.pdf",
        "mimeType": "application/pdf",
        "metadata": {"submission_id": 12345},
        "parentUuid": "12829224-2127-4494-abf7-7e92870332cf",
        "uuid": "16aae069-99b9-494f-948b-4c2057ec5551",
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
                mock_response._content = sirius_sup_docs_response.encode("UTF-8")

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

    def mock_get(url):

        import urllib.parse as urlparse

        mock_response = requests.Response()

        parsed = urlparse.urlparse(url)
        submission_id = urlparse.parse_qs(parsed.query)["metadata[submission_id]"][0]

        get_responses = {
            "11111": [],
            "22222": [
                {"uuid": "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0", "parentUuid": None}
            ],
            "55555": [
                {"uuid": "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0", "parentUuid": None},
                {
                    "uuid": "772a922c-2372-4bf4-8040-cb0bf4fb7ccf",
                    "parentUuid": "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0",
                },
                {
                    "uuid": "b9d242a2-6a4f-4f1e-9642-07cb18d36945",
                    "parentUuid": "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0",
                },
                {
                    "uuid": "168fb7de-e982-4bf4-a820-751ea529c5fc",
                    "parentUuid": "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0",
                },
            ],
        }

        try:
            mock_response.status_code = 200
            mock_response._content = json.dumps(get_responses[submission_id])
        except KeyError:
            mock_response.status_code = 500
            mock_response.json = None

        return mock_response

    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture
def patched_get_secret(monkeypatch):
    def mock_secret(*args, **kwargs):
        return "this_is_a_secret_string"

    monkeypatch.setattr(sirius_service, "get_secret", mock_secret)


@pytest.fixture
def patched_validate_event_fail(monkeypatch):
    def mock_invalid(*args, **kwargs):
        return False, ["file_name", "file_type"]

    monkeypatch.setattr(supporting_docs, "validate_event", mock_invalid)


@pytest.fixture
def patched_validate_event_success(monkeypatch):
    def mock_valid(*args, **kwargs):
        return True, []

    monkeypatch.setattr(supporting_docs, "validate_event", mock_valid)
