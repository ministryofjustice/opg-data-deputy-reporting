import json

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


@pytest.mark.parametrize(
    "example_sirius_response, expected_result",
    [
        (
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
                    "attributes": {"submission_id": 12345},
                }
            },
        ),
        (
            {"data": "this is all wrong"},
            {"data": "Error validating Sirius Public API response"},
        ),
    ],
)
def test_format_sirius_response(example_sirius_response, expected_result):
    result = format_sirius_response(example_sirius_response)

    assert result == expected_result


@pytest.mark.parametrize(
    "case_ref, expected_result",
    [
        (
            "valid_client_id",
            {
                "data": {
                    "type": "Report",
                    "id": "8ffdddb1-f19b-4c46-b4d1-9388ade95a68",
                    "attributes": {"submission_id": 12345},
                }
            },
        ),
        (
            "invalid_client_id",
            {"data": f"Error sending data to Sirius", "sirius_api_status_code": 400},
        ),
        (
            None,
            {"data": f"Error sending data to Sirius", "sirius_api_status_code": 500},
        ),
    ],
)
def test_submit_document_to_sirius(
    patched_requests, case_ref, expected_result, default_sirius_reports_request,
):
    headers = {"Content-Type": "application/json"}
    default_sirius_reports_request["caseRecNumber"] = case_ref
    body = json.dumps(default_sirius_reports_request)

    response = submit_document_to_sirius(url="", data=body, headers=headers)
    # response_supporting_docs = submit_document_to_sirius_supporting_docs(
    #     url="", data=body, headers=headers
    # )

    assert response == expected_result
    # assert response == response_supporting_docs


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
        ("banana", "not/a/real/route/", "random/endpoint/", False,),
    ],
)
def test_build_sirius_url(base_url, api_route, endpoint, expected_result):
    assert build_sirius_url(base_url, api_route, endpoint) == expected_result
    assert build_sirius_url(
        base_url, api_route, endpoint
    ) == build_sirius_url_supporting_docs(base_url, api_route, endpoint)


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
