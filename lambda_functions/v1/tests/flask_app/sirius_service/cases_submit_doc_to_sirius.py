import json

from pytest_cases import CaseData, cases_generator, case_tags

report_test_data = {
    "caseRecNumber": "1111",
    "type": "Report",
    "metadata": {"submission_id": 123},
    "file": {
        "name": "Report_1234567T_2018_2019_11111.pdf",
        "type": "application/pdf",
        "source": "string",
    },
}

suppdoc_test_data = {
    "caseRecNumber": "1111",
    "parentUuid": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
    "type": "Report - General",
    "metadata": {"submission_id": 123},
    "file": {
        "name": "Report_1234567T_2018_2019_11111.pdf",
        "type": "application/pdf",
        "source": "string",
    },
}


@case_tags("post_success")
@cases_generator(
    "Successful post to Sirius: {test_data}",
    test_data=[report_test_data, suppdoc_test_data],
)
def case_success(test_data) -> CaseData:

    data = json.dumps(test_data)
    method = "POST"
    endpoint = "documents"
    url_params = None

    expected_status_code = 201
    expected_response = {
        "data": {
            "attributes": {"submission_id": test_data["metadata"]["submission_id"]},
            "id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            "type": test_data["type"],
        }
    }
    if "parentUuid" in test_data:
        expected_response["data"]["attributes"]["parent_id"] = test_data["parentUuid"]
    else:
        expected_response["data"]["attributes"]["parent_id"] = None

    return (
        data,
        method,
        endpoint,
        url_params,
        expected_status_code,
        expected_response,
    )


@case_tags("post_error")
@cases_generator(
    "Post to Sirius with errors: {test_data}",
    test_data=[report_test_data, suppdoc_test_data],
)
def case_error(test_data) -> CaseData:

    data = json.dumps(test_data)
    method = "POST"
    endpoint = "documents"
    url_params = None

    expected_responses = {
        400: [
            "Payload validation failed in Sirius",
            "Could not verify URL params in Sirius",
        ],
        500: ["Unable to send document to Sirius", "Unknown error talking to Sirius"],
    }

    return (data, method, endpoint, url_params, expected_responses)


@case_tags("env_vars")
@cases_generator(
    "Env var not set {env_var}", env_var=["SIRIUS_BASE_URL", "API_VERSION"]
)
def case_missing_env_vars(env_var) -> CaseData:

    data = json.dumps(report_test_data)
    method = "POST"
    endpoint = "documents"
    url_params = None

    expected_status_code = 500
    expected_response = f"Expected environment variables not set, details: '{env_var}'"

    return (
        data,
        method,
        endpoint,
        url_params,
        env_var,
        expected_status_code,
        expected_response,
    )
