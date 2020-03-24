import json

import boto3
import jwt
import pytest
from botocore.exceptions import ClientError
from jwt import DecodeError
from moto import mock_secretsmanager

from lambda_functions.reports.reports import (
    submit_document_to_sirius,
    build_sirius_url,
    get_secret,
    build_sirius_headers,
)
from tests.helpers.use_test_data import is_valid_schema


@pytest.mark.parametrize(
    "case_ref, expected_result",
    [
        (
            "valid_client_id",
            {
                "status_code": 201,
                "body": '{"uuid": "531ca3b6-3f17-4ece-bdc5-7faf7f1f8427"}',
            },
        ),
        ("invalid_client_id", {"status_code": 400, "body": "Invalid payload"}),
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


# def test_sirius_does_not_exist(monkeypatch, sirius_request):
#     headers = {"Content-Type": "application/json"}
#     body = sirius_request
#
#     response = submit_document_to_sirius(
#         url="http://this_url_does_not_exist/", data=body, headers=headers
#     )
#
#     assert response["statusCode"] == 404


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


# @pytest.mark.parametrize(
#     "secret_code, environment, region",
#     [("i_am_a_secret_code", "development", "eu-west-1")],
# )
# @mock_secretsmanager
# def test_get_secret(secret_code, environment, region):
#     session = boto3.session.Session()
#     client = session.client(service_name="secretsmanager", region_name=region)
#
#     client.create_secret(Name=f"{environment}/jwt-key", SecretString=secret_code)
#     assert get_secret(environment) == secret_code
#
#     with pytest.raises(ClientError):
#         get_secret("not_a_real_environment")
