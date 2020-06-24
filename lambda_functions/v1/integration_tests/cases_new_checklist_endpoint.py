import random

from pytest_cases import CaseData, case_name

from lambda_functions.v1.integration_tests.conftest import generate_file_name

new_submission_id = random.randint(10000, 99999)


@case_name(
    "Successful post to new checklist endpoint - checklist is child of existing "
    "report sent in the same submission"
)
def case_success_original_IN_112(test_config: str) -> CaseData:

    print(f"Using test_config: {test_config['name']}")
    # Test Data

    report_id = test_config["report_id"]
    submission_id = test_config["submission_id"]
    case_ref = test_config["case_ref"]

    endpoint = f"clients/{case_ref}/reports/" f"{report_id}/checklists"

    url = f"{test_config['url']}/{endpoint}"

    method = "POST"
    payload = {
        "checklist": {
            "data": {
                "type": "supportingdocuments",
                "attributes": {"submission_id": submission_id},
                "file": {
                    "name": f"{generate_file_name()}.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }

    # Expected returns

    expected_status_code = 201
    expected_response_data = {
        # "type": "Report - Checklist",
        "type": "supportingdocuments",
        "submission_id": submission_id,
        "parent_id": None,
    }

    return url, method, payload, expected_status_code, expected_response_data


@case_name(
    "Successful post to new checklist endpoint - checklist is child of existing "
    "report sent in a different submission"
)
def case_success_new_submission_IN_112(test_config: str) -> CaseData:

    print(f"Using test_config: {test_config['name']}")
    # Test Data

    report_id = test_config["report_id"]
    submission_id = 54321
    case_ref = test_config["case_ref"]

    endpoint = f"clients/{case_ref}/reports/" f"{report_id}/checklists"
    url = f"{test_config['url']}/{endpoint}"

    method = "POST"
    payload = {
        "checklist": {
            "data": {
                "type": "supportingdocuments",
                "attributes": {"submission_id": submission_id},
                "file": {
                    "name": f"{generate_file_name()}.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }

    # Expected returns

    expected_status_code = 201
    expected_response_data = {
        # "type": "Report - Checklist",
        "type": "supportingdocuments",
        "submission_id": submission_id,
        "parent_id": None,
    }

    return url, method, payload, expected_status_code, expected_response_data
