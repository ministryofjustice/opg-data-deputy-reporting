import copy

from pytest_cases import CaseData

default_body = {
    "supporting_document": {
        "data": {
            "type": "supportingdocuments",
            "id": "443e881b-370a-4343-acb3-9965d341662f",
            "attributes": {
                "submission_id": 231231,
                "report_id": "443e881b-370a-4343-acb3-9965d341662f",
            },
            "file": {
                "name": "Supporting_Document_111.pdf",
                "mimetype": "application/pdf",
                "source": "string",
            },
        }
    }
}

default_case_ref = "12345678"

default_report_id = "443e881b-370a-4343-acb3-9965d341662f"


def case_happy_path() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        All data present, Sirius payload is populated as expected
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    report_id = default_report_id
    expected_result = (True, [])

    return body, case_ref, report_id, expected_result


def case_missing_required_field() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        Missing required field - filename
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    report_id = default_report_id
    expected_result = (False, ["file_name"])

    body["supporting_document"]["data"]["file"].pop("name")

    return body, case_ref, report_id, expected_result


def case_null_required_field() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        Null required field - filename
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    report_id = default_report_id
    expected_result = (False, ["file_name"])

    body["supporting_document"]["data"]["file"]["name"] = None
    return body, case_ref, report_id, expected_result


def case_empty_required_field() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        Empty required field - filename
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    report_id = default_report_id
    expected_result = (False, ["file_name"])

    body["supporting_document"]["data"]["file"]["name"] = ""

    return body, case_ref, report_id, expected_result


def case_missing_multiple_required_fields() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        Missing multiple required fields - file_type and file_source
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    report_id = default_report_id
    expected_result = (False, ["file_type", "file_source"])

    body["supporting_document"]["data"]["file"].pop("mimetype")
    body["supporting_document"]["data"]["file"].pop("source")

    return body, case_ref, report_id, expected_result


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
    report_id = default_report_id
    expected_result = (False, ["file_type", "file_source", "file_name"])

    body["supporting_document"]["data"]["file"]["name"] = None
    body["supporting_document"]["data"]["file"].pop("mimetype")
    body["supporting_document"]["data"]["file"]["source"] = ""

    return body, case_ref, report_id, expected_result
