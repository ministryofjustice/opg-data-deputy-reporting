import logging
import urllib

import boto3
import jwt
import pytest
from botocore.exceptions import ClientError
from jwt import DecodeError
from moto import mock_secretsmanager
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.flask_app.app.api import sirius_service
from lambda_functions.v1.functions.flask_app.app.api.sirius_service import (
    format_sirius_success,
    new_submit_document_to_sirius,
    handle_sirius_error,
)
from lambda_functions.v1.tests.flask_app.sirius_service import (
    cases_format_sirius_response,
    cases_submit_doc_to_sirius,
)

"""
Functions that require tests (* for done):

* build_sirius_url
* get_secret
* build_sirius_headers
new_post_to_sirius
* new_submit_document_to_sirius
* new_format_sirius_response
submit_document_to_sirius (superseded by the 'new_' functions above so ignoring)
"""


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
    ],
)
def test_build_sirius_url(base_url, version, endpoint, url_params, expected_result):
    # Copied directly from original
    # "lambda_functions/v1/tests/reports/test_reports_sirius_service.py' test
    url = sirius_service.build_sirius_url(base_url, version, endpoint, url_params)

    assert urllib.parse.unquote(url) == expected_result


def test_build_sirius_url_error():
    base_url = "banana"
    version = "30"
    endpoint = "random/endpoint/"
    url_params = None
    with pytest.raises(Exception):
        url = sirius_service.build_sirius_url(base_url, version, endpoint, url_params)

        print(f"url: {url}")

        assert 1 == 3


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
    # Copied directly from original
    # "lambda_functions/v1/tests/reports/test_reports_sirius_service.py' test
    if test_content_type:
        headers = sirius_service.build_sirius_headers(content_type=test_content_type)
    else:
        headers = sirius_service.build_sirius_headers()

    assert headers["Content-Type"] == expected_content_type


def test_build_sirius_headers_auth(patched_get_secret):
    # Copied directly from original
    # "lambda_functions/v1/tests/reports/test_reports_sirius_service.py' test
    headers = sirius_service.build_sirius_headers()
    token = headers["Authorization"].split()[1]

    try:
        jwt.decode(token.encode("UTF-8"), "this_is_a_secret_string", algorithms="HS256")
    except DecodeError as e:
        pytest.fail(f"JWT is not encoded properly: {e}")

    with pytest.raises(DecodeError):
        jwt.decode(token.encode("UTF-8"), "this_is_the_wrong_key", algorithms="HS256")


@pytest.mark.parametrize(
    "secret_code, environment, region",
    [("i_am_a_secret_code", "development", "eu-west-1")],
)
@mock_secretsmanager
def test_get_secret(secret_code, environment, region):
    # Copied directly from original
    # "lambda_functions/v1/tests/reports/test_reports_sirius_service.py' test

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region)

    client.create_secret(Name=f"{environment}/jwt-key", SecretString=secret_code)
    assert sirius_service.get_secret(environment) == secret_code

    with pytest.raises(ClientError):
        sirius_service.get_secret("not_a_real_environment")


@cases_data(module=cases_submit_doc_to_sirius, has_tag="post_success")
@pytest.mark.usefixtures("patched_get_secret", "patched_post")
def test_new_submit_document_to_sirius(monkeypatch, case_data: CaseDataGetter):
    (
        data,
        method,
        endpoint,
        url_params,
        env_var,
        expected_status_code,
        expected_response,
    ) = case_data.get()

    if env_var:
        monkeypatch.delenv(env_var)

    status_code, response = new_submit_document_to_sirius(
        data=data, method=method, endpoint=endpoint, url_params=url_params
    )

    assert response == expected_response


@cases_data(module=cases_submit_doc_to_sirius, has_tag="post_error")
@pytest.mark.usefixtures("patched_get_secret", "patched_post_broken_sirius")
def test_new_submit_document_to_sirius_errors(monkeypatch, case_data: CaseDataGetter):
    (data, method, endpoint, url_params, expected_responses) = case_data.get()

    status_code, response = new_submit_document_to_sirius(
        data=data, method=method, endpoint=endpoint, url_params=url_params
    )

    print(f"status_code: {status_code}")
    print(f"response: {response}")

    assert (
        any(message in response for message in expected_responses[status_code]) is True
    )


@cases_data(module=cases_format_sirius_response, has_tag="success")
def test_new_format_sirius_response(case_data: CaseDataGetter):
    (
        sirius_response_code,
        sirius_response,
        api_response_code,
        api_response,
    ) = case_data.get()

    formatted_status_code, formatted_response_text = format_sirius_success(
        sirius_response_code, sirius_response
    )

    assert formatted_response_text == api_response
    assert formatted_status_code == api_response_code


@cases_data(module=cases_format_sirius_response, has_tag="error")
def test_new_format_sirius_response_error(caplog, case_data: CaseDataGetter):
    (
        sirius_response_code,
        sirius_response,
        error_details,
        api_response_code,
        api_response,
    ) = case_data.get()

    formatted_status_code, formatted_response_text = handle_sirius_error(
        sirius_response_code, sirius_response, error_details
    )
    print(f"formatted_response_text: {formatted_response_text}")
    assert formatted_response_text == api_response
    assert formatted_status_code == api_response_code

    with caplog.at_level(logging.ERROR):
        assert api_response in caplog.text
