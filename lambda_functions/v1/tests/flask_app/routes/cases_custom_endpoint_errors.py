from pytest_cases import CaseData, case_tags, cases_generator

"""
400 because payload is messed up
405 wrong method
415 not application/json
"""

test_urls = [
    {"name": "reports", "method": "POST", "url": "1111/reports"},
    {
        "name": "supportingdocuments",
        "method": "POST",
        "url": "1111/reports/de26f80c-ed6d-4c52-b6bd-e0260bb0faf0/supportingdocuments",
    },
    {
        "name": "checklists",
        "method": "POST",
        "url": "1111/reports/de26f80c-ed6d-4c52-b6bd-e0260bb0faf0/checklists",
    },
    {
        "name": "checklists update",
        "method": "PUT",
        "url": "1111/reports/de26f80c-ed6d-4c52-b6bd-e0260bb0faf0/checklists/ea35592e-"
        "a1a7-4f87-98e9-1519bcb086ac",
    },
]


@case_tags("endpoint")
@cases_generator("Test custom 404 for {test_url} with wrong method", test_url=test_urls)
def case_405(test_url) -> CaseData:

    test_headers = {"Content-Type": "application/json"}
    test_data = ""
    test_method = "NOT POST"

    # Can't force it to raise a 405, wrong method can only seem to return a 404,
    # which is a legit error code so keeping it this way
    expected_response_status_code = 404
    expected_response_data = "OPGDATA-API-NOTFOUND"

    return (
        test_url,
        test_headers,
        test_data,
        test_method,
        expected_response_status_code,
        expected_response_data,
    )


@case_tags("endpoint")
@cases_generator("Test custom 415 for {test_url}", test_url=test_urls)
def case_415(test_url) -> CaseData:

    test_headers = {"Content-Type": "chipmunk/alvin"}
    test_data = ""
    test_method = test_url["method"]

    expected_response_status_code = 415
    expected_response_data = "OPGDATA-API-MEDIA"

    return (
        test_url,
        test_headers,
        test_data,
        test_method,
        expected_response_status_code,
        expected_response_data,
    )


@case_tags("endpoint")
@cases_generator("Test custom 400 not json payload for {test_url}", test_url=test_urls)
def case_400_not_json(test_url) -> CaseData:

    print(f"test_url: {test_url}")

    test_headers = {"Content-Type": "application/json"}
    test_data = {"i am not": "json"}
    test_method = test_url["method"]

    expected_response_status_code = 400
    expected_response_data = "OPGDATA-API-INVALIDREQUEST"

    return (
        test_url,
        test_headers,
        test_data,
        test_method,
        expected_response_status_code,
        expected_response_data,
    )
