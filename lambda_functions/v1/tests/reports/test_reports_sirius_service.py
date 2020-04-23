import json
import urllib.parse

import jwt
import pytest
from jwt import DecodeError

from lambda_functions.v1.functions.reports.app.sirius_service import (
    submit_document_to_sirius,
    build_sirius_url,
    build_sirius_headers,
    # get_secret,
    format_sirius_response,
)
from lambda_functions.v1.functions.supporting_docs.app.supporting_docs import (
    build_sirius_url as build_sirius_url_supporting_docs,
)


# import boto3
# from aws_xray_sdk.core import xray_recorder
# from botocore.exceptions import ClientError
# from moto import mock_secretsmanager


# TODO this does not work through CI, something to do with aws xray,
#  see https://github.com/aws/aws-xray-sdk-python/issues/155
# @pytest.mark.parametrize(
#     "secret_code, environment, region",
#     [("i_am_a_secret_code", "development", "eu-west-1")],
# )
# @mock_secretsmanager
# def test_get_secret(secret_code, environment, region):
#     # Disable sampling for tests, see github issue:
#     # https://github.com/aws/aws-xray-sdk-python/issues/155
#     xray_recorder.configure(sampling=False)
#
#     session = boto3.session.Session()
#     client = session.client(service_name="secretsmanager", region_name=region)
#
#     client.create_secret(Name=f"{environment}/jwt-key", SecretString=secret_code)
#     assert get_secret(environment) == secret_code
#
#     with pytest.raises(ClientError):
#         get_secret("not_a_real_environment")


# TODO this does not work through CI, something to do with aws xray,
#  see https://github.com/aws/aws-xray-sdk-python/issues/155
# def test_sirius_does_not_exist(monkeypatch, default_sirius_reports_request):
#     headers = {"Content-Type": "application/json"}
#     body = default_sirius_reports_request
#
#     response = submit_document_to_sirius(
#         url="http://this_url_does_not_exist/", data=body, headers=headers
#     )
#
#     assert response["statusCode"] == 404
from lambda_functions.v1.tests.helpers.use_test_data import is_valid_schema


@pytest.mark.parametrize(
    "example_sirius_response_code, example_sirius_response, expected_result",
    [
        (
            201,
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
            },
            {
                "data": {
                    "type": "Report",
                    "id": "8ffdddb1-f19b-4c46-b4d1-9388ade95a68",
                    "attributes": {"submission_id": 12345, "parent_id": None},
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
        assert is_valid_schema(result, "201_created_schema.json")
    else:
        assert is_valid_schema(result, "standard_error_schema.json")


@pytest.mark.parametrize(
    "case_ref, expected_response_body, expected_response_code",
    [
        (
            "valid_client_id",
            {
                "data": {
                    "type": "Report",
                    "id": "8ffdddb1-f19b-4c46-b4d1-9388ade95a68",
                    "attributes": {"submission_id": 12345, "parent_id": None},
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
def test_submit_document_to_sirius(
    patched_requests,
    case_ref,
    expected_response_body,
    expected_response_code,
    default_sirius_reports_request,
):
    headers = {"Content-Type": "application/json"}
    default_sirius_reports_request["caseRecNumber"] = case_ref
    body = json.dumps(default_sirius_reports_request)

    response = submit_document_to_sirius(url="", data=body, headers=headers)
    # response_supporting_docs = submit_document_to_sirius_supporting_docs(
    #     url="", data=body, headers=headers
    # )

    response_code, response_body = response

    assert response_code == expected_response_code
    assert response_body == expected_response_body
    # assert response == response_supporting_docs


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
    assert build_sirius_url(
        base_url, version, endpoint
    ) == build_sirius_url_supporting_docs(base_url, version, endpoint)


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
