import random

from pytest_cases import CaseData, case_name

from lambda_functions.v1.integration_tests.conftest import (
    config,
    uploaded_reports,
    uploaded_checklists,
)

new_submission_id = random.randint(10000, 99999)


@case_name(
    "Successful post to new checklist endpoint - checklist is child of existing "
    "report sent in the same submission"
)
def case_success_original_IN_112(base_url: str) -> CaseData:

    print(f"Using base_url: {base_url}")
    # Test Data

    report = random.choice(uploaded_reports)
    report_id = report["report_id"]
    submission_id = new_submission_id
    checklist_id = random.choice(
        [d["document_id"] for d in uploaded_checklists if d["amended"] is False]
    )
    endpoint = (
        f"clients/{config['GOOD_CASEREF']}/reports/"
        f"{report_id}/checklists/"
        f"{checklist_id}"
    )
    url = f"{base_url}/{endpoint}"

    print(f"report_id: {report_id}")
    print(f"submission_id: {submission_id}")
    print(f"checklist_id: {checklist_id}")

    method = "PUT"
    payload = {
        "checklist": {
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

    expected_status_code = 200
    expected_response_data = {
        "type": "Report",
        "submission_id": submission_id,
        "parent_id": report_id,
    }

    return url, method, payload, expected_status_code, expected_response_data
