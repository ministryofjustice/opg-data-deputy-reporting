from pytest_cases import CaseData, case_name, case_tags, cases_generator

"""
test successful post - 201
sirius not available
bad case ref
bad payload
missing env vars
bad secret
"""


@case_tags("endpoint")
@case_name("Successful post to Docs API")
def case_success() -> CaseData:

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
    expected_response_data = {"uuid": "5a8b1a26-8296-4373-ae61-f8d0b250e773"}

    return (
        test_data,
        test_headers,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
    )


@case_tags("endpoint")
@case_name("Case ref doesn't exist in Sirius")
def case_bad_params() -> CaseData:

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


# @case_tags("endpoint")
# @case_name("Bad payload sent to Docs API - no submission_id")
# def case_bad_data_attributes() -> CaseData:
#
#     test_data = {
#         "report": {
#             "data": {
#                 "type": "reports",
#                 "attributes": {
#                     "reporting_period_from": "2019-01-01",
#                     "reporting_period_to": "2019-12-31",
#                     "year": 2019,
#                     "date_submitted": "2020-01-03T09:30:00.001Z",
#                     "type": "PF",
#                 },
#                 "file": {
#                     "name": "Report_1234567T_2018_2019_11111.pdf",
#                     "mimetype": "application/pdf",
#                     "source": "string",
#                 },
#             }
#         }
#     }
#     test_case_ref = 1111
#
#     test_headers = {"Content-Type": "application/json"}
#
#     expected_response_status_code = 400
#     expected_response_data = "unable to parse payload"
#
#     return (
#         test_data,
#         test_headers,
#         test_case_ref,
#         expected_response_status_code,
#         expected_response_data,
#     )


# @case_tags("endpoint")
# @cases_generator(
#     "Bad payload sent to Docs API - no file {file_data}",
#     file_data=["name", "mimetype", "source"],
# )
# def case_bad_data_file(file_data) -> CaseData:
#
#     default_test_data = {
#         "report": {
#             "data": {
#                 "type": "reports",
#                 "attributes": {
#                     "submission_id": 12345,
#                     "reporting_period_from": "2019-01-01",
#                     "reporting_period_to": "2019-12-31",
#                     "year": 2019,
#                     "date_submitted": "2020-01-03T09:30:00.001Z",
#                     "type": "PF",
#                 },
#                 "file": {
#                     "name": "Report_1234567T_2018_2019_11111.pdf",
#                     "mimetype": "application/pdf",
#                     "source": "string",
#                 },
#             }
#         }
#     }
#
#     test_data = copy.deepcopy(default_test_data)
#     del test_data["report"]["data"]["file"][file_data]
#
#     test_case_ref = 1111
#
#     test_headers = {"Content-Type": "application/json"}
#
#     expected_response_status_code = 400
#     expected_response_data = "unable to parse payload"
#
#     return (
#         test_data,
#         test_headers,
#         test_case_ref,
#         expected_response_status_code,
#         expected_response_data,
#     )


@case_tags("environment")
@cases_generator(
    "Missing environment variables - {ev}", ev=["SIRIUS_BASE_URL", "API_VERSION"]
)
def case_missing_env_vars(ev) -> CaseData:

    env_var = ev
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
