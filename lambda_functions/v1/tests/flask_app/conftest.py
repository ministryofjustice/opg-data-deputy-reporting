import json

import pytest
import requests

import lambda_functions
from lambda_functions.v1.functions.flask_app.app import api
from lambda_functions.v1.functions.flask_app.app.api import sirius_service

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
def default_report_request_body_flask():
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
def default_sirius_checklist_request(
    default_request_case_ref, default_request_report_id
):
    return {
        "type": "Report - Checklist",
        "caseRecNumber": default_request_case_ref,
        "metadata": {"submission_id": 231231, "report_id": default_request_report_id},
        "file": {
            "name": "Supporting_Document_111.pdf",
            "source": "string",
            "type": "application/pdf",
        },
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


@pytest.fixture()
def default_sirius_supporting_docs_request_with_parent_id(
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
        "parentUuid": "5783a7ad-9251-4cc7-80e3-c411c3bd87e0",
    }


@pytest.fixture(autouse=True)
def default_supporting_doc_request_body_flask(default_request_report_id):
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
    monkeypatch.setenv("SIRIUS_BASE_URL", "http://not-really-sirius.com")
    monkeypatch.setenv("SIRIUS_PUBLIC_API_URL", "api/public/v1/")
    monkeypatch.setenv("LOGGER_LEVEL", "DEBUG")
    monkeypatch.setenv("JWT_SECRET", "THIS_IS_MY_SECRET_KEY")
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("SESSION_DATA", "publicapi@opgtest.com")
    monkeypatch.setenv("API_VERSION", "flask")


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
def patched_requests_flask(monkeypatch):
    def mock_post(*args, **kwargs):
        print("MOCK POST")
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

    def mock_get(*args, **kwargs):
        print("MOCK GET")
        url = kwargs["url"]
        mock_response = requests.Response()

        if url == "https://frontend-feature5.dev.sirius.opg.digital/":
            mock_response.status_code = 200
            mock_response._content = json.dumps([{"data": "success"}]).encode("UTF-8")
        else:
            mock_response.status_code = 200
            mock_response._content = json.dumps([{"data": "success"}]).encode("UTF-8")
            # mock_response.status_code = 500
            # mock_response._content = None

        return mock_response

    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture()
def patched_get_secret(monkeypatch):
    def mock_secret(*args, **kwargs):
        print("I AM A FAKE SECRET")
        return "this_is_a_secret_string"

    monkeypatch.setattr(sirius_service, "get_secret", mock_secret)


@pytest.fixture
def patched_send_get_to_sirius(monkeypatch):
    def mock_response(url):
        import urllib.parse as urlparse

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

            mock_response = get_responses[submission_id]
        except KeyError:
            mock_response = None

        return mock_response

    monkeypatch.setattr(sirius_service, "send_get_to_sirius", mock_response)


@pytest.fixture()
def patched_submit_document_to_sirius(monkeypatch):
    def mock_submit_document_to_sirius(*args, **kwargs):
        print("FAKE POST TO SIRIUS")

        try:
            data = json.loads(kwargs["data"])
            print(f"data: {data}")
        except (KeyError, TypeError) as e:
            print(f"error getting post data: {e}")

        try:
            case_ref = json.loads(kwargs["data"])["caseRecNumber"]
            print(f"case_ref from conftest: {case_ref}")
        except (KeyError, TypeError) as e:
            print(f"error getting caseRecNumber: {e}")

        response_code = 404
        response_data = {
            "data": {
                "type": "",
                "id": "",
                "attributes": {"submission_id": "", "parent_id": ""},
            }
        }

        print(f"(response_code, response_data): {(response_code, response_data)}")
        return (response_code, response_data)

    monkeypatch.setattr(
        lambda_functions.v1.functions.flask_app.app.api.sirius_service,
        "submit_document_to_sirius",
        mock_submit_document_to_sirius,
    )


valid_case_refs = ["1111", "2222", "3333"]


@pytest.fixture(autouse=False, params=[201])
def patched_post(monkeypatch, request):
    def mock_post_to_sirius(*args, **kwargs):
        print("Mock post to Sirius")
        data = json.loads(kwargs["data"])

        mock_response = requests.Response()
        mock_response.status_code = request.param

        def json_func():
            doc_type = data["type"]
            file_name = data["file"]["name"]
            mimetype = data["file"]["type"]
            metadata = data["metadata"]
            payload = {
                "type": doc_type,
                "filename": file_name,
                "mimetype": mimetype,
                "metadata": metadata,
                "uuid": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
                # "parentUuid": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            }
            if "parentUuid" in data:
                payload["parentUuid"] = "5a8b1a26-8296-4373-ae61-f8d0b250e773"

            return payload

        mock_response.json = json_func

        return mock_response.status_code, mock_response.json()

    monkeypatch.setattr(api.sirius_service, "new_post_to_sirius", mock_post_to_sirius)


# @pytest.fixture(autouse=False, params=[400, 404, 500])
@pytest.fixture(autouse=False)
def patched_post_broken_sirius(request, monkeypatch):
    def mock_post_to_broken_sirius(*args, **kwargs):
        print("MOCK POST TO BROKEN SIRIUS")

        data = json.loads(kwargs["data"])
        case_ref = data["caseRecNumber"]

        mock_response = requests.Response()
        mock_response.status_code = request.param

        # if case_ref in valid_case_refs:
        mock_response.status_code = request.param

        if mock_response.status_code == 400 and case_ref in valid_case_refs:

            def json_func():
                payload = {
                    "validation_errors": {},
                    "type": "http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html",
                    "title": "Bad Request",
                    "status": "400",
                    "detail": "Payload failed validation, details of what failed here",
                    "instance": "string",
                }

                return payload

        elif mock_response.status_code == 400 and case_ref not in valid_case_refs:

            def json_func():
                return {
                    "type": "http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html",
                    "title": "Bad Request",
                    "status": 400,
                    "detail": f'Client referenced by court reference "{case_ref}" was '
                    f"not found",
                }

        elif mock_response.status_code == 404:

            def json_func():
                return {
                    "validation_errors": {},
                    "type": "http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html",
                    "title": "Not Found",
                    "status": "404",
                    "detail": "Route does not exist",
                    "instance": "string",
                }

        else:

            def json_func():
                return {
                    "validation_errors": {},
                    "type": "http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html",
                    "title": "Not Found",
                    "status": mock_response.status_code,
                    "detail": "This is a generic Sirius error",
                    "instance": "string",
                }

        mock_response.json = json_func
        print(f"mock_response.json: {mock_response.json}")

        return mock_response.status_code, mock_response.json()

    monkeypatch.setattr(
        api.sirius_service, "new_post_to_sirius", mock_post_to_broken_sirius
    )
