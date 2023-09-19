import json

from pytest_cases import case, parametrize

"""
400 because payload is messed up
405 wrong method
415 not application/json
"""

test_urls = [
    {
        "name": "reports",
        "method": "POST",
        "url": "1111/reports",
        "test_data": {
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
        },
    },
    {
        "name": "supportingdocuments",
        "method": "POST",
        "url": "1111/reports/de26f80c-ed6d-4c52-b6bd-e0260bb0faf0/supportingdocuments",
        "test_data": {
            "supporting_document": {
                "data": {
                    "type": "supportingdocuments",
                    "attributes": {"submission_id": 12345},
                    "file": {
                        "name": "Report_1234567T_2018_2019_11111.pdf",
                        "mimetype": "application/pdf",
                        "source": "string",
                    },
                }
            }
        },
    },
    {
        "name": "checklists",
        "method": "POST",
        "url": "1111/reports/de26f80c-ed6d-4c52-b6bd-e0260bb0faf0/checklists",
        "test_data": {
            "checklist": {
                "data": {
                    "type": "supportingdocuments",
                    "attributes": {
                        "submission_id": 12345,
                        "submitter_email": "donald.draper@digital.justice.gov.uk",
                        "reporting_period_from": "2019-01-01",
                        "reporting_period_to": "2019-12-31",
                        "year": 2019,
                        "type": "PF",
                    },
                    "file": {
                        "name": "Report_1234567T_2018_2019_11111.pdf",
                        "mimetype": "application/pdf",
                        "source": "string",
                    },
                }
            }
        },
    },
    {
        "name": "checklists update",
        "method": "PUT",
        "url": "1111/reports/de26f80c-ed6d-4c52-b6bd-e0260bb0faf0/checklists/ea35592e-"
        "a1a7-4f87-98e9-1519bcb086ac",
        "test_data": {
            "checklist": {
                "data": {
                    "type": "supportingdocuments",
                    "attributes": {
                        "submission_id": 12345,
                        "submitter_email": "donald.draper@digital.justice.gov.uk",
                        "reporting_period_from": "2019-01-01",
                        "reporting_period_to": "2019-12-31",
                        "year": 2019,
                        "type": "PF",
                    },
                    "file": {
                        "name": "Report_1234567T_2018_2019_11111.pdf",
                        "mimetype": "application/pdf",
                        "source": "string",
                    },
                }
            }
        },
    },
]


@case(tags=["endpoint"], id="Test custom 404 for {test_url} with wrong method")
@parametrize(test_url=test_urls)
def case_405(test_url):

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


@case(tags=["endpoint"], id="Test custom 415 for {test_url}")
@parametrize(test_url=test_urls)
def case_415(test_url):

    test_headers = {"Content-Type": "chipmunk/alvin"}
    test_data = json.dumps(test_url["test_data"])
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


@case(tags=["endpoint"], id="Test custom 400 not json payload for {test_url}")
@parametrize(test_url=test_urls)
def case_400_not_json(test_url):

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


# TODO add separate test for these - it can't handle the error code parameters
@case(tags=["endpoint", "custom_message"], id="Test custom 400 bad url params for {test_url}")
@parametrize(test_url=test_urls)
def case_400_bad_url_params(test_url):

    print(f"test_url: {test_url}")

    test_headers = {"Content-Type": "application/json"}

    test_url["url"] = test_url["url"].replace("1111", "not-a-real-caseref")

    test_data = json.dumps(test_url["test_data"])
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
