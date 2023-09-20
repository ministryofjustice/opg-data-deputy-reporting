from pytest_cases import case, parametrize
    # cases_generator

"""
test successful post - 201
sirius not available
bad case ref
bad payload
missing env vars
bad secret
"""


@case(tags=["endpoint", "success"], id="Successful post to Docs API")
def case_success():

    test_data = {
        "report": {
            "data": {
                "type": "reports",
                "attributes": {
                    "submission_id": 12345,
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
    test_case_ref = 1111

    test_headers = {"Content-Type": "application/json"}

    expected_response_status_code = 201
    expected_response_data = {
        "data": {
            "attributes": {"submission_id": 12345, "parent_id": None},
            "id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            # "type": "Report",
            "type": "reports",
        }
    }

    return (
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_response_data)


@case(tags=["endpoint", "success"], id="Successful post to Docs API using s3 ref")
def case_success_s3():

    test_data = {
        "report": {
            "data": {
                "type": "reports",
                "attributes": {
                    "submission_id": 12345,
                    "reporting_period_from": "2019-01-01",
                    "reporting_period_to": "2019-12-31",
                    "year": 2019,
                    "date_submitted": "2020-01-03T09:30:00.001Z",
                    "type": "PF",
                },
                "file": {
                    "name": "Report_1234567T_2018_2019_11111.pdf",
                    "mimetype": "application/pdf",
                    "s3_reference": "this_is_a_file_on_s3.pdf",
                },
            }
        }
    }
    test_case_ref = 1111

    test_headers = {"Content-Type": "application/json"}

    expected_response_status_code = 201
    expected_response_data = {
        "data": {
            "attributes": {"submission_id": 12345, "parent_id": None},
            "id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            "type": "reports",
        }
    }

    return (
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
    )


@case(tags=["endpoint", "success"], id="Successful post to Docs API - with both source and s3 ref")
def case_both_s3_and_file():

    test_data = {
        "report": {
            "data": {
                "type": "reports",
                "attributes": {
                    "submission_id": 12345,
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
                    "s3_reference": "this_is_a_file_on_s3.pdf",
                },
            }
        }
    }
    test_case_ref = 1111

    test_headers = {"Content-Type": "application/json"}

    expected_response_status_code = 201
    expected_response_data = {
        "data": {
            "attributes": {"submission_id": 12345, "parent_id": None},
            "id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            "type": "reports",
        }
    }

    return (
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
    )


@case(tags=["endpoint", "error"], id="Fail post to Docs API - with neither source nor s3 ref")
def case_neither_s3_nor_file():

    test_data = {
        "report": {
            "data": {
                "type": "reports",
                "attributes": {
                    "submission_id": 12345,
                    "reporting_period_from": "2019-01-01",
                    "reporting_period_to": "2019-12-31",
                    "year": 2019,
                    "date_submitted": "2020-01-03T09:30:00.001Z",
                    "type": "PF",
                },
                "file": {
                    "name": "Report_1234567T_2018_2019_11111.pdf",
                    "mimetype": "application/pdf",
                },
            }
        }
    }
    test_case_ref = 1111

    test_headers = {"Content-Type": "application/json"}

    expected_response_status_code = 400
    expected_response_data = "OPGDATA-API-INVALIDREQUEST"

    return (
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
    )


@case(tags=["endpoint", "error"], id="Case ref doesn't exist in Sirius")
def case_bad_params():

    test_data = {
        "report": {
            "data": {
                "type": "reports",
                "attributes": {
                    "submission_id": 12345,
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
    test_case_ref = "not-a-real-caseref"

    test_headers = {"Content-Type": "application/json"}

    expected_response_status_code = 400
    expected_response_data = "OPGDATA-API-INVALIDREQUEST"

    return (
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
    )


@case(tags=["environment"], id="Successful post to Docs API - with both source and s3 ref")
def case_missing_env_vars():

    env_var = "SIRIUS_BASE_URL"
    test_data = {
        "report": {
            "data": {
                "type": "reports",
                "attributes": {
                    "submission_id": 12345,
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
    test_case_ref = 1111

    test_headers = {"Content-Type": "application/json"}

    expected_response_status_code = 500
    expected_logger_message = f"'{env_var}' not set"

    return (
        env_var,
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_logger_message,
    )
