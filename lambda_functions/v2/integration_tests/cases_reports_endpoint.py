from pytest_cases import CaseData, case_name


# submission_id = config["SUBMISSION_ID"]
from lambda_functions.v2.integration_tests.conftest import generate_file_name


@case_name("Successful post to reports endpoint")
def case_success_original(test_config: str) -> CaseData:

    # Test Data

    submission_id = test_config["submission_id"]

    endpoint = f"clients/{test_config['case_ref']}/reports"
    url = f"{test_config['url']}/{endpoint}"

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
        "type": "reports",
        "submission_id": submission_id,
        "parent_id": None,
    }

    return url, method, payload, expected_status_code, expected_response_data
