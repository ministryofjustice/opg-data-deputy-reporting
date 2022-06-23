import random

from pytest_cases import CaseData, case_name

from integration_tests.v2.conftest import generate_file_name

new_submission_id = random.randint(10000, 99999)


@case_name(
    "Successful post to new checklist endpoint - checklist is child of existing "
    "report sent in the same submission"
)
def case_success_original_IN_112(test_config: str) -> CaseData:

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
                "type": "checklists",
                "attributes": {
                    "submission_id": submission_id,
                    "submitter_email": "donald.draper@digital.justice.gov.uk",
                    "reporting_period_from": "2019-01-01",
                    "reporting_period_to": "2019-12-31",
                    "year": 2019,
                    "type": "PF",
                },
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
        "type": "checklists",
        "submission_id": submission_id,
        "parent_id": None,
    }

    return url, method, payload, expected_status_code, expected_response_data


@case_name(
    "Successful post to new checklist endpoint - checklist is child of existing "
    "report sent in a different submission"
)
def case_success_new_submission_IN_112(test_config: str) -> CaseData:

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
                "type": "checklists",
                "attributes": {
                    "submission_id": submission_id,
                    "submitter_email": "donald.draper@digital.justice.gov.uk",
                    "reporting_period_from": "2019-01-01",
                    "reporting_period_to": "2019-12-31",
                    "year": 2019,
                    "type": "PF",
                },
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
        "type": "checklists",
        "submission_id": submission_id,
        "parent_id": None,
    }

    return url, method, payload, expected_status_code, expected_response_data
