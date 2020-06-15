import random

from pytest_cases import CaseData, case_name

new_submission_id = random.randint(10000, 99999)


@case_name("Successful update of a checklist")
def case_success_original_IN_112(test_config: str) -> CaseData:

    print(f"Using test_config: {test_config['name']}")
    # Test Data

    report_id = test_config["report_id"]
    submission_id = 54321
    case_ref = test_config["case_ref"]
    checklist_id = test_config["checklist_id"]

    endpoint = (
        f"clients/{case_ref}/reports/" f"{report_id}/checklists/" f"{checklist_id}"
    )
    url = f"{test_config['url']}/{endpoint}"

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
        "type": "Report - Checklist",
        "submission_id": submission_id,
        "original_checklist_id": checklist_id,
    }

    return url, method, payload, expected_status_code, expected_response_data
