import datetime
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
    create_record,
    configs_to_test,
    update_record,
    all_records,
)


# @pytest.mark.skip(reason="don't run in CI")
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

    print(f"response: {response}")

    assert status == expected_status_code
    assert type(response) == str
    if status == 201:
        r = json.loads(response)

        file_name = payload["report"]["data"]["file"]["name"]

        test_config["report_id"] = r["data"]["id"]

        create_record(returned_data=r, file_name=file_name)

        assert r["data"]["type"] == expected_response_data["type"]
        assert is_valid_uuid(r["data"]["id"])
        returned_submission_id = r["data"]["attributes"]["submission_id"]
        assert returned_submission_id == expected_response_data["submission_id"]
        assert (
            r["data"]["attributes"]["parent_id"] == expected_response_data["parent_id"]
        )


# @pytest.mark.skip(reason="don't run in CI")
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

    r = json.loads(response)
    print(f"r: {r}")

    assert status == expected_status_code
    assert type(response) == str
    if status == 201:
        r = json.loads(response)
        file_name = payload["supporting_document"]["data"]["file"]["name"]

        test_config["supp_doc_id"] = r["data"]["id"]

        create_record(returned_data=r, file_name=file_name)

        assert r["data"]["type"] == expected_response_data["type"]
        assert is_valid_uuid(r["data"]["id"])
        returned_submission_id = r["data"]["attributes"]["submission_id"]
        assert returned_submission_id == expected_response_data["submission_id"]
        if "parent_id" in expected_response_data:
            returned_parent_id = r["data"]["attributes"]["parent_id"]
            assert returned_parent_id == expected_response_data["parent_id"]


@pytest.mark.skip(reason="don't run in CI")
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

        file_name = payload["checklist"]["data"]["file"]["name"]
        test_config["checklist_id"] = r["data"]["id"]

        create_record(returned_data=r, file_name=file_name)

        assert r["data"]["type"] == expected_response_data["type"]
        assert is_valid_uuid(r["data"]["id"])
        returned_submission_id = r["data"]["attributes"]["submission_id"]
        assert returned_submission_id == expected_response_data["submission_id"]
        assert (
            r["data"]["attributes"]["parent_id"] == expected_response_data["parent_id"]
        )


@pytest.mark.skip(reason="don't run in CI")
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

        update_record(
            returned_data=r,
            original_record_id=expected_response_data["original_checklist_id"],
        )

        assert r["data"]["type"] == expected_response_data["type"]
        assert is_valid_uuid(r["data"]["id"])
        returned_submission_id = r["data"]["attributes"]["submission_id"]
        assert returned_submission_id == expected_response_data["submission_id"]


# @pytest.mark.skip(reason="don't run in CI")
@pytest.mark.run(order=5)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_confirm_data(test_config):

    assert len(all_records) > 0

    for row in all_records:
        row["config_used"] = test_config["name"]

    filename = datetime.datetime.now().strftime("%Y-%m-%d")
    json_records = json.dumps(all_records, indent=4)

    with open(f"{filename}_updates.json", "w") as outfile:
        outfile.write(json_records)
