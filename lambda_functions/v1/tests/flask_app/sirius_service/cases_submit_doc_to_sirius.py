import json

from pytest_cases import case_name, CaseData, cases_generator, case_tags

test_data = {
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
@case_name("Successful post to Sirius")
def case_success() -> CaseData:

    data = json.dumps(test_data)
    method = "POST"
    endpoint = "documents"
    url_params = None
    env_var = None

    expected_status_code = 201
    expected_response = {
        "data": {
            "attributes": {
                "parent_id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
                "submission_id": 123,
            },
            "id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            "type": "Report - General",
        }
    }

    return (
        data,
        method,
        endpoint,
        url_params,
        env_var,
        expected_status_code,
        expected_response,
    )


@case_tags("post_error")
@case_name("Successful post to Sirius, but Sirius returns an error code")
def case_error() -> CaseData:

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


@case_tags("post_success")
@cases_generator(
    "Env var not set {env_var}", env_var=["SIRIUS_BASE_URL", "API_VERSION"]
)
def case_missing_env_vars(env_var) -> CaseData:

    data = json.dumps(test_data)
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
