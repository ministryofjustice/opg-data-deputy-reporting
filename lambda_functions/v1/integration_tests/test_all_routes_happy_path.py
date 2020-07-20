import json

import pytest
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.integration_tests import (
    cases_reports_endpoint,
    cases_supporting_docs_endpoint,
    cases_new_checklist_endpoint,
    cases_update_checklist_endpoint,
)
from lambda_functions.v1.integration_tests.conftest import (
    send_a_request,
    is_valid_uuid,
    configs_to_test,
)


@pytest.mark.smoke_test
@pytest.mark.run(order=1)
@pytest.mark.parametrize("test_config", configs_to_test)
@cases_data(module=cases_reports_endpoint)
def test_post_a_report(case_data: CaseDataGetter, test_config):
    (
        url,
        method,
        payload,
        expected_status_code,
        expected_response_data,
    ) = case_data.get(test_config)

    status, response = send_a_request(
        url=url, method=method, payload=payload, test_config=test_config
    )

    assert status == expected_status_code
    assert type(response) == str
    if status == 201:
        r = json.loads(response)

        test_config["report_id"] = r["data"]["id"]

        assert r["data"]["type"] == expected_response_data["type"]
        assert is_valid_uuid(r["data"]["id"])
        returned_submission_id = r["data"]["attributes"]["submission_id"]
        assert returned_submission_id == expected_response_data["submission_id"]

        assert (
            r["data"]["attributes"]["parent_id"] == expected_response_data["parent_id"]
        )


@pytest.mark.smoke_test
@pytest.mark.run(order=2)
@pytest.mark.parametrize("test_config", configs_to_test)
@cases_data(module=cases_supporting_docs_endpoint)
def test_post_a_supporting_doc(case_data: CaseDataGetter, test_config):
    (
        url,
        method,
        payload,
        expected_status_code,
        expected_response_data,
    ) = case_data.get(test_config)

    status, response = send_a_request(
        url=url, method=method, payload=payload, test_config=test_config
    )

    assert status == expected_status_code
    assert type(response) == str
    if status == 201:
        r = json.loads(response)

        test_config["supp_doc_id"] = r["data"]["id"]

        assert r["data"]["type"] == expected_response_data["type"]
        assert is_valid_uuid(r["data"]["id"])
        returned_submission_id = r["data"]["attributes"]["submission_id"]
        assert returned_submission_id == expected_response_data["submission_id"]
        if "parent_id" in expected_response_data:
            returned_parent_id = r["data"]["attributes"]["parent_id"]
            assert returned_parent_id == expected_response_data["parent_id"]


@pytest.mark.smoke_test
@pytest.mark.run(order=3)
@pytest.mark.parametrize("test_config", configs_to_test)
@cases_data(module=cases_new_checklist_endpoint)
def test_post_a_new_checklist(case_data: CaseDataGetter, test_config):
    (
        url,
        method,
        payload,
        expected_status_code,
        expected_response_data,
    ) = case_data.get(test_config)

    status, response = send_a_request(
        url=url, method=method, payload=payload, test_config=test_config
    )

    assert status == expected_status_code
    assert type(response) == str
    if status == 201:
        r = json.loads(response)
        test_config["checklist_id"] = r["data"]["id"]

        assert r["data"]["type"] == expected_response_data["type"]
        assert is_valid_uuid(r["data"]["id"])
        returned_submission_id = r["data"]["attributes"]["submission_id"]
        assert returned_submission_id == expected_response_data["submission_id"]
        assert (
            r["data"]["attributes"]["parent_id"] == expected_response_data["parent_id"]
        )


@pytest.mark.smoke_test
@pytest.mark.run(order=4)
@pytest.mark.parametrize("test_config", configs_to_test)
@cases_data(module=cases_update_checklist_endpoint)
def test_post_an_updated_checklist(case_data: CaseDataGetter, test_config):
    (
        url,
        method,
        payload,
        expected_status_code,
        expected_response_data,
    ) = case_data.get(test_config)

    status, response = send_a_request(
        url=url, method=method, payload=payload, test_config=test_config
    )

    assert status == expected_status_code
    assert type(response) == str
    if status == 200:
        r = json.loads(response)

        assert r["data"]["type"] == expected_response_data["type"]
        assert is_valid_uuid(r["data"]["id"])
        returned_submission_id = r["data"]["attributes"]["submission_id"]
        assert returned_submission_id == expected_response_data["submission_id"]
