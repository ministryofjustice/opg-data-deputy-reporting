import copy

from pytest_cases import CaseData

default_body = {
    "checklist": {
        "data": {
            "type": "checklists",
            "attributes": {"submission_id": 231231, "report_id": "not a real id"},
            "file": {
                "name": "Checklist.pdf",
                "mimetype": "application/pdf",
                "source": "string",
            },
        }
    }
}

default_case_ref = "12345678"

default_report_id = "443e881b-370a-4343-acb3-9965d341662f"

nondigital_report_id = "99999999-9999-9999-9999-999999999999"


def case_happy_path() -> CaseData:
    """
    Data for checklists endpoint tests

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
    expected_result = (False, ["checklist->data->attributes->file->name"])

    body["checklist"]["data"]["file"].pop("name")

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
    expected_result = (False, ["checklist->data->attributes->file->name"])

    body["checklist"]["data"]["file"]["name"] = None
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
    expected_result = (False, ["checklist->data->attributes->file->name"])

    body["checklist"]["data"]["file"]["name"] = ""

    return body, case_ref, report_id, expected_result


def case_missing_multiple_required_fields() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        Missing multiple required fields - file_mimetype and file_name
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    report_id = default_report_id
    expected_result = (
        False,
        [
            "checklist->data->attributes->file->mimetype",
            "checklist->data->attributes->file->name",
        ],
    )

    body["checklist"]["data"]["file"].pop("mimetype")
    body["checklist"]["data"]["file"].pop("name")

    return body, case_ref, report_id, expected_result


def case_bad_multiple_required_fields() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        null file_name
        missing file_type
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    report_id = default_report_id
    expected_result = (
        False,
        [
            "checklist->data->attributes->file->name",
            "checklist->data->attributes->file->mimetype",
        ],
    )

    body["checklist"]["data"]["file"]["name"] = None
    body["checklist"]["data"]["file"].pop("mimetype")

    return body, case_ref, report_id, expected_result


def case_submission_id_is_missing() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        missing submission_id
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    report_id = default_report_id
    expected_result = (
        True,
        [],
    )

    body["checklist"]["data"]["attributes"].pop("submission_id")

    return body, case_ref, report_id, expected_result


def case_submission_id_is_null() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        null submission_id
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    report_id = default_report_id
    expected_result = (
        True,
        [],
    )

    body["checklist"]["data"]["attributes"]["submission_id"] = None

    return body, case_ref, report_id, expected_result


def case_submission_id_is_empty() -> CaseData:
    """
    Data for reports endpoint tests

    Returns:
        empty string submission_id
    """

    body = copy.deepcopy(default_body)
    case_ref = default_case_ref
    report_id = default_report_id
    expected_result = (
        True,
        [],
    )

    body["checklist"]["data"]["attributes"]["submission_id"] = ""

    return body, case_ref, report_id, expected_result
