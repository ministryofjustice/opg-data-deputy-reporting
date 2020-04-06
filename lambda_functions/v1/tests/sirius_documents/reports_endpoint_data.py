from pytest_cases import CaseData

default_body = {
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

default_case_ref = "12345678"

default_expected_result = {
    "type": "Report - General",
    "caseRecNumber": "12345678",
    "metadata": {
        "submission_id": 12345,
        "reporting_period_from": "2019-01-01",
        "reporting_period_to": "2019-12-31",
        "year": 2019,
        "date_submitted": "2020-01-03T09:30:00.001Z",
        "type": "PF",
    },
    "file": {
        "name": "Report_1234567T_2018_2019_11111.pdf",
        "source": "string",
        "type": "application/pdf",
    },
}


def case_happy_path() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        All data present, Sirius payload is populated as expected
    """

    body = default_body
    case_ref = default_case_ref
    expected_result = default_expected_result

    return body, case_ref, expected_result


def case_missing_filename() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        Missing filename
    """

    body = default_body
    case_ref = default_case_ref
    expected_result = default_expected_result

    body["report"]["data"]["file"].pop("name")

    expected_result["file"]["name"] = "value not present"

    return body, case_ref, expected_result


def case_null_filename() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        Null filename
    """

    body = default_body
    case_ref = default_case_ref
    expected_result = default_expected_result

    body["report"]["data"]["file"]["name"] = None

    expected_result["file"]["name"] = None

    return body, case_ref, expected_result


def case_empty_filename() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        Empty filename
    """

    body = default_body
    case_ref = default_case_ref
    expected_result = default_expected_result

    body["report"]["data"]["file"]["name"] = ""

    expected_result["file"]["name"] = ""

    return body, case_ref, expected_result
