import json
import urllib.parse

import jwt
import pytest
from jwt import DecodeError

from lambda_functions.v1.functions.checklists.app.sirius_service import (
    submit_document_to_sirius,
    build_sirius_url,
    build_sirius_headers,
    # get_secret,
    format_sirius_response,
    send_get_to_sirius,
)

from lambda_functions.v1.tests.helpers.use_test_data import is_valid_schema


@pytest.mark.parametrize(
    "example_sirius_response_code, example_sirius_response, expected_result",
    [
        (
            201,
            {
                "type": "Report - Checklist",
                "filename": "b11a291e6dae6_supportingDoc123.pdf",
                "mimeType": "application/pdf",
                "metadata": {
                    "submission_id": 12345,
                    "report_id": "b6279263-9834-40a6-84c1-a0e7d7e13dbf",
                    "is_checklist": True
                },
                "uuid": "16aae069-99b9-494f-948b-4c2057ec5551",
            },
            {
                "data": {
                    "type": "Report - Checklist",
                    "id": "16aae069-99b9-494f-948b-4c2057ec5551",
                    "attributes": {
                        "submission_id": 12345,
                        "report_id": "b6279263-9834-40a6-84c1-a0e7d7e13dbf",
                        "is_checklist": True
                    },
                }
            },
        ),
        (
            201,
            {
                "type": "Report - Checklist",
                "filename": "b11a291e6dae6_supportingDoc123.pdf",
                "mimeType": "application/pdf",
                "metadata": {
                    "is_checklist": True
                },
                "uuid": "99999999-9999-9999-9999-999999999999",
            },
            {
                "data": {
                    "type": "Report - Checklist",
                    "id": "99999999-9999-9999-9999-999999999999",
                    "attributes": {
                        "is_checklist": True
                    },
                }
            },
        ),
        (
            500,
            {"data": "this is all wrong"},
            {
                "errors": {
                    "id": "",
                    "code": "OPGDATA-API-SERVERERROR",
                    "detail": "Something unexpected happened internally",
                    "meta": {},
                    "title": "Internal server error",
                }
            },
        ),
    ],
)
def test_format_sirius_response(
    example_sirius_response_code, example_sirius_response, expected_result
):
    result = format_sirius_response(
        example_sirius_response, example_sirius_response_code
    )

    assert result == expected_result
    if example_sirius_response_code == 201:
        assert is_valid_schema(result, "201_created_schema_checklist.json")
    else:
        assert is_valid_schema(result, "standard_error_schema.json")


@pytest.mark.parametrize(
    "case_ref, expected_response_body, expected_response_code",
    [
        (
            "valid_client_id",
            {
                "data": {
                    "type": "Report - Checklist",
                    "id": "16aae069-99b9-494f-948b-4c2057ec5551",
                    "attributes": {
                        "submission_id": 12345,
                    },
                }
            },
            201,
        ),
        (
            "invalid_client_id",
            {
                "errors": {
                    "id": "",
                    "code": "OPGDATA-API-INVALIDREQUEST",
                    "title": "Invalid Request",
                    "detail": "Invalid request, the data is incorrect",
                    "meta": {},
                }
            },
            400,
        ),
        (
            None,
            {
                "errors": {
                    "id": "",
                    "code": "OPGDATA-API-SERVERERROR",
                    "title": "Internal server error",
                    "detail": "Something unexpected happened internally",
                    "meta": {},
                }
            },
            500,
        ),
    ],
)
def test_post_document_to_sirius(
    patched_requests,
    case_ref,
    expected_response_body,
    expected_response_code,
    default_sirius_checklists_request,
):
    headers = {"Content-Type": "application/json"}
    default_sirius_checklists_request["caseRecNumber"] = case_ref
    body = json.dumps(default_sirius_checklists_request)

    response = submit_document_to_sirius(
        method="POST", url="", data=body, headers=headers
    )

    response_code, response_body = response

    assert response_code == expected_response_code
    assert response_body == expected_response_body


@pytest.mark.parametrize(
    "base_url, version, endpoint, url_params, expected_result",
    [
        (
            "https://frontend-feature5.dev.sirius.opg.digital/api/public",
            "v1",
            "documents",
            None,
            "https://frontend-feature5.dev.sirius.opg.digital/api/public"
            "/v1/documents",
        ),
        (
            "https://frontend-feature5.dev.sirius.opg.digital/api/public",
            "v1",
            "clients/12345678/reports/7230e5a2-312b-4b50-bc09-f9c00c6b7f1d",
            None,
            "https://frontend-feature5.dev.sirius.opg.digital/api/public/v1/clients/123"
            "45678/reports/7230e5a2-312b-4b50-bc09-f9c00c6b7f1d",
        ),
        (
            "https://frontend-feature5.dev.sirius.opg.digital/api/public",
            "v1",
            "clients/12345678/documents",
            {
                "metadata[submission_id]": 11111,
                "metadata[report_id]": "d0a43b67-3084-4a74-ab55-a7542cfadd37",
            },
            "https://frontend-feature5.dev.sirius.opg.digital/api/public/v1/clients/123"
            "45678/documents?metadata[submission_id]=11111&metadata[report_id]=d0a43b67"
            "-3084-4a74-ab55-a7542cfadd37",
        ),
        (
            "https://frontend-feature5.dev.sirius.opg.digital/api/public",
            "v1",
            "documents",
            {
                "casrecnumber": "e4e497bc-7744-47ab-9d1a-345412640161",
                "metadata[submission_id]": 11111,
                "metadata[report_id]": "d0a43b67-3084-4a74-ab55-a7542cfadd37",
            },
            "https://frontend-feature5.dev.sirius.opg.digital/api/public/v1"
            "/documents?casrecnumber=e4e497bc-7744-47ab-9d1a-345412640161"
            "&metadata[submission_id]=11111&metadata["
            "report_id]=d0a43b67"
            "-3084-4a74-ab55-a7542cfadd37",
        ),
        (
            "http://www.fake_url.com",
            "6.3.1",
            "random/endpoint/",
            None,
            "http://www.fake_url.com/6.3.1/random/endpoint/",
        ),
        ("banana", "30", "random/endpoint/", None, False,),
    ],
)
def test_build_sirius_url(base_url, version, endpoint, url_params, expected_result):
    url = build_sirius_url(base_url, version, endpoint, url_params)
    try:
        assert urllib.parse.unquote(url) == expected_result
    except TypeError:
        assert url == expected_result


@pytest.mark.parametrize(
    "test_content_type, test_secret_key, expected_content_type",
    [
        (None, "this_is_a_secret_string", "application/json"),
        ("application/json", "this_is_a_secret_string", "application/json"),
        ("application/pdf", "this_is_a_secret_string", "application/pdf"),
    ],
)
def test_build_sirius_headers_content_type(
    patched_get_secret, test_content_type, test_secret_key, expected_content_type
):
    if test_content_type:
        headers = build_sirius_headers(content_type=test_content_type)
    else:
        headers = build_sirius_headers()

    assert headers["Content-Type"] == expected_content_type


def test_build_sirius_headers_auth(patched_get_secret):
    headers = build_sirius_headers()
    token = headers["Authorization"].split()[1]

    try:
        jwt.decode(token.encode("UTF-8"), "this_is_a_secret_string", algorithms="HS256")
    except DecodeError as e:
        pytest.fail(f"JWT is not encoded properly: {e}")

    with pytest.raises(DecodeError):
        jwt.decode(token.encode("UTF-8"), "this_is_the_wrong_key", algorithms="HS256")


@pytest.mark.parametrize(
    "url, expected_result",
    [
        ("https://frontend-feature5.dev.sirius.opg.digital/", [{"data": "success"}]),
        ("https://fake_url.com", None),
    ],
)
def test_get_endpoint(
    patched_requests, patched_get_secret, url, expected_result,
):
    result = send_get_to_sirius(url)
    print(result)

    assert result == expected_result