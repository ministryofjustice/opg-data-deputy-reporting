import json

import jwt
import pytest
from jwt import DecodeError

from lambda_functions.v1.functions.reports.app.sirius_service import (
    submit_document_to_sirius,
    build_sirius_url,
    build_sirius_headers,
    # get_secret,
)
from lambda_functions.v1.functions.supporting_docs.app.supporting_docs import (
    build_sirius_url as build_sirius_url_supporting_docs,
)
from lambda_functions.v1.functions.supporting_docs.app.supporting_docs import (
    submit_document_to_sirius as submit_document_to_sirius_supporting_docs,
)
from lambda_functions.v1.tests.helpers.use_test_data import is_valid_schema


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


@pytest.mark.parametrize(
    "case_ref, logger_message, expected_result",
    [
        (
            "valid_client_id",
            "Document successfully send to Sirius",
            {
                "status_code": 201,
                "body": '{"uuid": "531ca3b6-3f17-4ece-bdc5-7faf7f1f8427"}',
            },
        ),
        ("invalid_client_id", "", {"status_code": 400, "body": "Invalid payload"}),
        (None, "", {"status_code": 500, "body": "Invalid payload"}),
    ],
)
def test_submit_document_to_sirius(
    patched_requests,
    case_ref,
    logger_message,
    expected_result,
    default_sirius_reports_request,
):
    headers = {"Content-Type": "application/json"}
    default_sirius_reports_request["caseRecNumber"] = case_ref
    body = json.dumps(default_sirius_reports_request)

    response = submit_document_to_sirius(url="", data=body, headers=headers)
    response_supporting_docs = submit_document_to_sirius_supporting_docs(
        url="", data=body, headers=headers
    )

    assert response["statusCode"] == expected_result["status_code"]
    # assert response["body"] == expected_result["body"]
    assert is_valid_schema(json.dumps(response), "standard_lambda_response_schema.json")
    assert response == response_supporting_docs


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
