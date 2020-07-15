import json

import pytest
import requests

from lambda_functions.v2.functions.checklists.app import sirius_service, checklists

test_data = {
    "valid_clients": ["valid_client_id", "0319392T", "12345678", "22814959"],
    "invalid_clients": ["invalid_client_id"],
}


@pytest.fixture(autouse=True)
def default_sirius_checklists_request(
    default_request_case_ref, default_request_report_id
):
    return {
        "type": "Report - Checklist",
        "caseRecNumber": default_request_case_ref,
        "metadata": {"submission_id": 231231, "report_id": default_request_report_id, "is_checklist": "true"},
        "file": {
            "name": "checklist.pdf",
            "source": "string",
            "type": "application/pdf",
        },
    }


@pytest.fixture(autouse=True)
def sirius_checklists_request_with_no_report_submission(
    default_request_case_ref,
    nondigital_request_report_id
):
    return {
        "type": "Report - Checklist",
        "caseRecNumber": default_request_case_ref,
        "metadata": {"report_id": nondigital_request_report_id, "is_checklist": "true"},
        "file": {
            "name": "checklist.pdf",
            "source": "string",
            "type": "application/pdf",
        },
    }


@pytest.fixture(autouse=True)
def default_checklists_request_body(default_request_report_id):
    return {
        "checklist": {
            "data": {
                "type": "checklists",
                "id": default_request_report_id,
                "attributes": {"submission_id": 231231},
                "file": {
                    "name": "checklist.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }


@pytest.fixture(autouse=True)
def checklists_request_body_with_no_report_submission(nondigital_request_report_id):
    return {
        "checklist": {
            "data": {
                "type": "checklists",
                "id": nondigital_request_report_id,
                "attributes": {},
                "file": {
                    "name": "checklist.pdf",
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
def nondigital_request_report_id():
    return "99999999-9999-9999-9999-999999999999"


@pytest.fixture(autouse=True)
def mock_env_setup(monkeypatch):
    monkeypatch.setenv("BASE_URL", "http://localhost:8080")
    monkeypatch.setenv("SIRIUS_BASE_URL", "http://sirius_url.com")
    monkeypatch.setenv("SIRIUS_PUBLIC_API_URL", "api/public/v1/")
    monkeypatch.setenv("LOGGER_LEVEL", "DEBUG")
    monkeypatch.setenv("JWT_SECRET", "THIS_IS_MY_SECRET_KEY")
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("SESSION_DATA", "publicapi@opgtest.com")
    monkeypatch.setenv("API_VERSION", "v2")


sirius_checklists_response = json.dumps(
    {
        "type": "Report - Checklist",
        "filename": "b11a291e6dae6_checklist.pdf",
        "mimeType": "application/pdf",
        "metadata": {"submission_id": 12345},
        "uuid": "16aae069-99b9-494f-948b-4c2057ec5551"
    }
)


@pytest.fixture
def patched_requests(monkeypatch):
    def mock_post(*args, **kwargs):
        print("MOCK POST")
        data = kwargs["data"]

        mock_response = requests.Response()

        try:
            if json.loads(data)["caseRecNumber"] in test_data["valid_clients"]:
                mock_response.status_code = 201
                mock_response._content = sirius_checklists_response.encode("UTF-8")
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

    def mock_get(*args, **kwargs):
        url = kwargs["url"]
        mock_response = requests.Response()

        if url == "https://frontend-feature5.dev.sirius.opg.digital/":
            mock_response.status_code = 200
            mock_response._content = json.dumps([{"data": "success"}]).encode("UTF-8")
        else:
            mock_response.status_code = 500
            mock_response._content = None

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

    monkeypatch.setattr(checklists, "validate_event", mock_invalid)


@pytest.fixture
def patched_validate_event_success(monkeypatch):
    def mock_valid(*args, **kwargs):
        return True, []

    monkeypatch.setattr(checklists, "validate_event", mock_valid)