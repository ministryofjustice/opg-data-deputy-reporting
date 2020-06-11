import random

from pytest_cases import CaseData, case_name

from lambda_functions.v1.integration_tests.conftest import (
    config,
    uploaded_reports,
    uploaded_supporting_docs,
)

new_submission_id = random.randint(10000, 99999)


@case_name(
    "Successful post to supporting docs endpoint - doc is child of existing "
    "report sent in the same submission"
)
def case_success_original(base_url: str) -> CaseData:

    print(f"Using base_url: {base_url}")
    # Test Data

    report = random.choice(uploaded_reports)
    report_id = report["report_id"]
    submission_id = report["submission_id"]
    endpoint = (
        f"clients/{config['GOOD_CASEREF']}/reports/" f"{report_id}/supportingdocuments"
    )
    url = f"{base_url}/{endpoint}"

    method = "POST"
    payload = {
        "supporting_document": {
            "data": {
                "type": "supportingdocuments",
                "attributes": {"submission_id": submission_id},
                "file": {
                    "name": "Report_1234567T_2018_2019_11111.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }

    # Expected returns

    expected_status_code = 201
    expected_response_data = {
        "type": "Report - General",
        "submission_id": submission_id,
        "parent_id": report_id,
        "report_id": report_id,
    }

    return url, method, payload, expected_status_code, expected_response_data


@case_name(
    "Successful post to supporting docs endpoint - doc is child of existing "
    "report sent in a different submission"
)
def case_success_new_submission(base_url: str) -> CaseData:

    print(f"Using base_url: {base_url}")
    # Test Data

    report = random.choice(uploaded_reports)
    report_id = report["report_id"]
    submission_id = new_submission_id

    endpoint = (
        f"clients/{config['GOOD_CASEREF']}/reports/" f"{report_id}/supportingdocuments"
    )
    url = f"{base_url}/{endpoint}"

    method = "POST"
    payload = {
        "supporting_document": {
            "data": {
                "type": "supportingdocuments",
                "attributes": {"submission_id": submission_id},
                "file": {
                    "name": "Report_1234567T_2018_2019_11111.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }

    # Expected returns

    expected_status_code = 201
    expected_response_data = {
        "type": "Report - General",
        "submission_id": submission_id,
        "parent_id": None,
        "report_id": report_id,
    }

    return url, method, payload, expected_status_code, expected_response_data


@case_name(
    "Successful post to supporting docs endpoint - doc is child of existing "
    "supporting doc "
)
def case_success_new_submission_child(base_url: str) -> CaseData:

    print(f"Using base_url: {base_url}")
    # Test Data

    report = random.choice(uploaded_reports)
    report_id = report["report_id"]
    submission_id = new_submission_id
    parent_id = [
        i["document_id"]
        for i in uploaded_supporting_docs
        if i["submission_id"] == submission_id
    ]

    endpoint = (
        f"clients/{config['GOOD_CASEREF']}/reports/" f"{report_id}/supportingdocuments"
    )
    url = f"{base_url}/{endpoint}"

    method = "POST"
    payload = {
        "supporting_document": {
            "data": {
                "type": "supportingdocuments",
                "attributes": {"submission_id": submission_id},
                "file": {
                    "name": "Report_1234567T_2018_2019_11111.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }

    # Expected returns

    expected_status_code = 201
    expected_response_data = {
        "type": "Report - General",
        "submission_id": submission_id,
        "parent_id": parent_id[0],
        "report_id": report_id,
    }

    return url, method, payload, expected_status_code, expected_response_data
