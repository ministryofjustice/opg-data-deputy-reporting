from pytest_cases import CaseData, case_name

from integration_tests.v2.conftest import generate_file_name


@case_name(
    "Successful post to reports endpoint "
    "Digideps S3 bucket ref sent instead of file source"
)
def case_success_s3(test_config: str) -> CaseData:

    submission_id = 11111

    endpoint = f"clients/{test_config['case_ref']}/reports"
    url = f"{test_config['url']}/{endpoint}"
    s3_object_key = test_config["s3_object_key"]

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
                    "name": f"s3{generate_file_name()}.pdf",
                    "mimetype": "application/pdf",
                    "s3_reference": s3_object_key,
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


@case_name(
    "Successful post to reports endpoint. Digideps S3 bucket ref AND file source sent"
)
def case_success_original_s3(test_config: str) -> CaseData:

    submission_id = 11111

    endpoint = f"clients/{test_config['case_ref']}/reports"
    url = f"{test_config['url']}/{endpoint}"
    s3_object_key = test_config["s3_object_key"]

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
                    "name": f"both{generate_file_name()}.pdf",
                    "mimetype": "application/pdf",
                    "s3_reference": s3_object_key,
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
                    "name": f"source{generate_file_name()}.pdf",
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
