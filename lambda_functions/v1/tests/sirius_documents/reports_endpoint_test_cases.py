import copy

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


def case_happy_path() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        All data present, Sirius payload is populated as expected
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    expected_result = (True, [])

    return body, case_ref, expected_result


def case_missing_required_field() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        Missing required field - filename
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    expected_result = (False, ["file_name"])

    body["report"]["data"]["file"].pop("name")

    return body, case_ref, expected_result


def case_null_required_field() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        Null required field - filename
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    expected_result = (False, ["file_name"])

    body["report"]["data"]["file"]["name"] = None

    return body, case_ref, expected_result


def case_empty_required_field() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        Empty required field - filename
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    expected_result = (False, ["file_name"])

    body["report"]["data"]["file"]["name"] = ""

    return body, case_ref, expected_result


def case_missing_multiple_required_fields() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        Missing multiple required fields - file_type and file_source
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    expected_result = (False, ["file_type", "file_source"])

    body["report"]["data"]["file"].pop("mimetype")
    body["report"]["data"]["file"].pop("source")

    return body, case_ref, expected_result


def case_bad_multiple_required_fields() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        null file_name
        missing file_type
        empty file_source
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    expected_result = (False, ["file_type", "file_source", "file_name"])

    body["report"]["data"]["file"]["name"] = None
    body["report"]["data"]["file"].pop("mimetype")
    body["report"]["data"]["file"]["source"] = ""

    return body, case_ref, expected_result
