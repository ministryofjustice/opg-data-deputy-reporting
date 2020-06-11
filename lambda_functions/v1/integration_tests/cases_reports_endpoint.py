from random import randint

from pytest_cases import CaseData, case_name

from lambda_functions.v1.integration_tests.conftest import config

# submission_id = config["SUBMISSION_ID"]


@case_name("Successful post to reports endpoint")
def case_success_original(base_url: str) -> CaseData:

    print(f"Using base_url: {base_url}")

    # Test Data

    submission_id = randint(100, 999)
    endpoint = f"clients/{config['GOOD_CASEREF']}/reports"
    url = f"{base_url}/{endpoint}"

    method = "POST"
    payload = {
        "report": {
            "data": {
                "type": "reports",
                "attributes": {
                    "submission_id": submission_id,
                    "reporting_period_from": "2019-01-01",
                    "reporting_period_to": "2019-12-31",
                    "year": 2019,
                    "date_submitted": "2020-01-03T09:30:00.001Z",
                    "type": "PF",
                },
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
        "type": "Report",
        "submission_id": submission_id,
        "parent_id": None,
    }

    return url, method, payload, expected_status_code, expected_response_data
