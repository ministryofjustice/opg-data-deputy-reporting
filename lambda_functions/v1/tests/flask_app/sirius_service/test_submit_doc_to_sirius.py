import pytest
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.flask_app.app.api.sirius_service import (
    new_submit_document_to_sirius,
)
from lambda_functions.v1.tests.flask_app.sirius_service import (
    cases_submit_doc_to_sirius,
)


@cases_data(module=cases_submit_doc_to_sirius, has_tag="post_success")
@pytest.mark.usefixtures("patched_get_secret", "patched_post")
def test_submit_success(monkeypatch, case_data: CaseDataGetter):
    (
        data,
        method,
        endpoint,
        url_params,
        expected_status_code,
        expected_response,
    ) = case_data.get()

    status_code, response = new_submit_document_to_sirius(
        data=data, method=method, endpoint=endpoint, url_params=url_params
    )

    assert response == expected_response


@cases_data(module=cases_submit_doc_to_sirius, has_tag="env_vars")
@pytest.mark.usefixtures("patched_get_secret", "patched_post")
def test_submit_env_vars_broken(monkeypatch, case_data: CaseDataGetter):
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
def test_submit_errors(monkeypatch, case_data: CaseDataGetter):
    (data, method, endpoint, url_params, expected_responses) = case_data.get()

    status_code, response = new_submit_document_to_sirius(
        data=data, method=method, endpoint=endpoint, url_params=url_params
    )

    print(f"status_code: {status_code}")
    print(f"response: {response}")

    assert (
        any(message in response for message in expected_responses[status_code]) is True
    )
