import json

import pytest

from lambda_functions.reports.reports import submit_document_to_sirius, build_sirius_url
from tests.helpers.use_test_data import is_valid_schema, load_data


@pytest.mark.parametrize(
    "case_ref, expected_result",
    [
        (
            "valid_client_id",
            {
                "status_code": 201,
                "body": {"uuid": "531ca3b6-3f17-4ece-bdc5-7faf7f1f8427"},
            },
        ),
        ("invalid_client_id", {"status_code": 400, "body": "Invalid Casrec ID"}),
    ],
)
def test_submit_document_to_sirius(
    patched_requests, case_ref, expected_result, sirius_request
):
    headers = {"Content-Type": "application/json"}
    sirius_request["caseRecNumber"] = case_ref
    body = json.dumps(sirius_request)

    response = submit_document_to_sirius(url="", data=body, headers=headers)


    assert response["statusCode"] == expected_result["status_code"]
    assert response["body"] == expected_result["body"]
    assert is_valid_schema(json.dumps(response), "lambda_response.json")


def test_sirius_does_not_exist(monkeypatch, sirius_request):
    headers = {"Content-Type": "application/json"}
    body = sirius_request

    response = submit_document_to_sirius(
        url="http://this_url_does_not_exist/", data=body, headers=headers
    )

    assert response["statusCode"] == 404


@pytest.mark.parametrize(
    "base_url, api_route, endpoint, expected_result",
    [
        (
            "https://frontend-feature5.dev.sirius.opg.digital/",
            "/api/public/v1/",
            "documents",
            "https://frontend-feature5.dev.sirius.opg.digital/api/public"
            "/v1/documents",
        ),
        (
            "http://www.fake_url.com",
            "not/a/real/route/",
            "random/endpoint/",
            "http://www.fake_url.com/not/a/real/route/random/endpoint/",
        ),
    ],
)
def test_build_sirius_url(base_url, api_route, endpoint, expected_result):
    assert build_sirius_url(base_url, api_route, endpoint) == expected_result


def test_build_sirius_headers():
    pass
