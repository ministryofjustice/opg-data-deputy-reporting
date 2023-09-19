import pytest
from pytest_cases import parametrize_with_cases

from lambda_functions.v2.functions.documents.app.api.sirius_service import (
    new_submit_document_to_sirius,
)
from lambda_functions.v2.tests.sirius_service import cases_submit_doc_to_sirius


@pytest.mark.usefixtures("patched_get_secret", "patched_post")
@parametrize_with_cases(
    "data,method,endpoint,url_params,expected_status_code,expected_response",
    cases=cases_submit_doc_to_sirius, has_tag="post_success"
)
def test_submit_success(
        monkeypatch,
        data,
        method,
        endpoint,
        url_params,
        expected_status_code,
        expected_response,
):

    status_code, response = new_submit_document_to_sirius(
        data=data, method=method, endpoint=endpoint, url_params=url_params
    )

    assert response == expected_response


@pytest.mark.usefixtures("patched_get_secret", "patched_post")
@parametrize_with_cases(
    "data,method,endpoint,url_params,env_var,expected_status_code,expected_response",
    cases=cases_submit_doc_to_sirius, has_tag="env_vars"
)
def test_submit_env_vars_broken(
        monkeypatch,
        data,
        method,
        endpoint,
        url_params,
        env_var,
        expected_status_code,
        expected_response,
):

    if env_var:
        monkeypatch.delenv(env_var)

    status_code, response = new_submit_document_to_sirius(
        data=data, method=method, endpoint=endpoint, url_params=url_params
    )

    assert expected_response in response


@pytest.mark.usefixtures("patched_get_secret", "patched_post_broken_sirius")
@parametrize_with_cases(
    "data,method,endpoint,url_params,expected_responses",
    cases=cases_submit_doc_to_sirius, has_tag="post_error"
)
def test_submit_errors(monkeypatch, data, method, endpoint, url_params, expected_responses):

    status_code, response = new_submit_document_to_sirius(
        data=data, method=method, endpoint=endpoint, url_params=url_params
    )

    print(f"status_code: {status_code}")
    print(f"response: {response}")

    assert (
        any(message in response for message in expected_responses[status_code]) is True
    )
