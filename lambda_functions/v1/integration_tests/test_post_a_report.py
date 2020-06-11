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
    uploaded_reports,
    urls_to_test,
    uploaded_supporting_docs,
    uploaded_checklists,
)


# @pytest.mark.skip(reason="don't run in CI")
@pytest.mark.run(order=1)
@pytest.mark.parametrize("base_url", urls_to_test)
@cases_data(module=cases_reports_endpoint)
def test_post_a_report(case_data: CaseDataGetter, base_url):
    (
        url,
        method,
        payload,
        expected_status_code,
        expected_response_data,
    ) = case_data.get(base_url)

    status, response = send_a_request(url=url, method=method, payload=payload)

    assert status == expected_status_code
    assert type(response) == str
    if status == 201:
        r = json.loads(response)
        assert r["data"]["type"] == expected_response_data["type"]
        assert is_valid_uuid(r["data"]["id"])
        returned_submission_id = r["data"]["attributes"]["submission_id"]
        assert returned_submission_id == expected_response_data["submission_id"]
        assert (
            r["data"]["attributes"]["parent_id"] == expected_response_data["parent_id"]
        )

        uploaded_reports.append(
            {
                "report_id": r["data"]["id"],
                "submission_id": r["data"]["attributes"]["submission_id"],
            }
        )


# @pytest.mark.skip(reason="don't run in CI")
@pytest.mark.run(order=2)
@pytest.mark.parametrize("base_url", urls_to_test)
@cases_data(module=cases_supporting_docs_endpoint)
def test_post_a_supporting_doc(case_data: CaseDataGetter, base_url):
    (
        url,
        method,
        payload,
        expected_status_code,
        expected_response_data,
    ) = case_data.get(base_url)

    status, response = send_a_request(url=url, method=method, payload=payload)

    assert status == expected_status_code
    assert type(response) == str
    if status == 201:
        r = json.loads(response)
        assert r["data"]["type"] == expected_response_data["type"]
        assert is_valid_uuid(r["data"]["id"])
        returned_submission_id = r["data"]["attributes"]["submission_id"]
        assert returned_submission_id == expected_response_data["submission_id"]
        assert (
            r["data"]["attributes"]["parent_id"] == expected_response_data["parent_id"]
        )

        uploaded_supporting_docs.append(
            {
                "document_id": r["data"]["id"],
                "submission_id": r["data"]["attributes"]["submission_id"],
                "parent_id": r["data"]["attributes"]["parent_id"],
            }
        )


# @pytest.mark.skip(reason="don't run in CI")
@pytest.mark.run(order=3)
@pytest.mark.parametrize("base_url", urls_to_test)
@cases_data(module=cases_new_checklist_endpoint)
def test_post_a_new_checklist(case_data: CaseDataGetter, base_url):
    (
        url,
        method,
        payload,
        expected_status_code,
        expected_response_data,
    ) = case_data.get(base_url)

    status, response = send_a_request(url=url, method=method, payload=payload)

    assert status == expected_status_code
    assert type(response) == str
    if status == 201:
        r = json.loads(response)
        assert r["data"]["type"] == expected_response_data["type"]
        assert is_valid_uuid(r["data"]["id"])
        returned_submission_id = r["data"]["attributes"]["submission_id"]
        assert returned_submission_id == expected_response_data["submission_id"]
        assert (
            r["data"]["attributes"]["parent_id"] == expected_response_data["parent_id"]
        )

        uploaded_checklists.append(
            {
                "document_id": r["data"]["id"],
                "submission_id": r["data"]["attributes"]["submission_id"],
                "parent_id": r["data"]["attributes"]["parent_id"],
                "amended": False,
            }
        )


# @pytest.mark.skip(reason="don't run in CI")
@pytest.mark.run(order=4)
@pytest.mark.parametrize("base_url", urls_to_test)
@cases_data(module=cases_update_checklist_endpoint)
def test_post_an_updated_checklist(case_data: CaseDataGetter, base_url):
    (
        url,
        method,
        payload,
        expected_status_code,
        expected_response_data,
    ) = case_data.get(base_url)

    status, response = send_a_request(url=url, method=method, payload=payload)

    assert status == expected_status_code
    assert type(response) == str
    if status == 201:
        r = json.loads(response)
        assert r["data"]["type"] == expected_response_data["type"]
        assert is_valid_uuid(r["data"]["id"])
        returned_submission_id = r["data"]["attributes"]["submission_id"]
        assert returned_submission_id == expected_response_data["submission_id"]
        assert (
            r["data"]["attributes"]["parent_id"] == expected_response_data["parent_id"]
        )

        checklist_id = r["data"]["id"]
        updated_checklist = list(
            filter(lambda c: c["document_id"] == checklist_id, uploaded_checklists)
        )[0]

        updated_checklist["amended"] = True


# @pytest.mark.skip(reason="don't run in CI")
@pytest.mark.run(order=3)
def test_confirm_data():
    print(f"uploaded_reports: {uploaded_reports}")
    print(f"uploaded_supporting_docs: {uploaded_supporting_docs}")

    assert len(uploaded_reports) > 0
    assert len(uploaded_supporting_docs) > 0
