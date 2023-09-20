import copy

from pytest_cases import case, parametrize

from integration_tests.v2.conftest import generate_file_name

default_report_payload = {
    "report": {
        "data": {
            "type": "reports",
            "attributes": {
                "submission_id": 1234,
                "reporting_period_from": "2019-01-01",
                "reporting_period_to": "2019-12-31",
                "year": 2019,
                "date_submitted": "2020-01-03T09:30:00.001Z",
                "type": "PF",
            },
            "file": {
                "name": f"{generate_file_name()}.pdf",
                "mimetype": "application/pdf",
                "source": "string",
            },
        }
    }
}

default_supdocs_payload = {
    "supporting_document": {
        "data": {
            "type": "supportingdocuments",
            "attributes": {"submission_id": 1234},
            "file": {
                "name": f"{generate_file_name()}.pdf",
                "mimetype": "application/pdf",
                "source": "string",
            },
        }
    }
}

default_checklist_payload = {
    "checklist": {
        "data": {
            "type": "supportingdocuments",
            "attributes": {"submission_id": 1234},
            "file": {
                "name": f"{generate_file_name()}.pdf",
                "mimetype": "application/pdf",
                "source": "string",
            },
        }
    }
}


@case(id="Bad payload sent to reports POST endpoint - missing data: {missing}")
@parametrize(
    missing=[
        "type",
        "attributes/submission_id",
        "file/name",
        "file/mimetype",
        # "file/source",
    ]
)
def case_reports_missing_fields(test_config: str, missing):

    endpoint = f"clients/{test_config['case_ref']}/reports"
    url = f"{test_config['url']}/{endpoint}"
    method = "POST"

    payload = copy.deepcopy(default_report_payload)

    if "/" in missing:
        del payload["report"]["data"][missing.split("/")[0]][missing.split("/")[1]]
    else:
        del payload["report"]["data"][missing]

    expected_status_code = 400

    return url, method, payload, expected_status_code


@case(id="Bad payload sent to reports POST endpoint - empty data: {missing}")
@parametrize(
    missing=[
        "type",
        "attributes/submission_id",
        "file/name",
        "file/mimetype",
        "file/source",
    ],
)
def case_reports_empty_fields(test_config: str, missing):

    endpoint = f"clients/{test_config['case_ref']}/reports"
    url = f"{test_config['url']}/{endpoint}"
    method = "POST"

    payload = copy.deepcopy(default_report_payload)

    if "/" in missing:
        payload["report"]["data"][missing.split("/")[0]][missing.split("/")[1]] = ""
    else:
        payload["report"]["data"][missing] = ""

    expected_status_code = 400

    return url, method, payload, expected_status_code


@case(id="Bad payload sent to supp docs POST endpoint - missing data: {missing}")
@parametrize(
    missing=[
        "attributes/submission_id",
        "file/name",
        "file/mimetype",
        # "file/source"
    ],
)
def case_suppdocs_missing_fields(test_config: str, missing):

    report_id = test_config["report_id"]
    case_ref = test_config["case_ref"]

    endpoint = f"clients/{case_ref}/reports/" f"{report_id}/supportingdocuments"
    url = f"{test_config['url']}/{endpoint}"
    method = "POST"

    payload = copy.deepcopy(default_supdocs_payload)

    if "/" in missing:
        del payload["supporting_document"]["data"][missing.split("/")[0]][
            missing.split("/")[1]
        ]
    else:
        del payload["supporting_document"]["data"][missing]

    expected_status_code = 400

    return url, method, payload, expected_status_code


@case(id="Bad payload sent to supp docs POST endpoint - empty data: {missing}")
@parametrize(
    missing=[
        "attributes/submission_id",
        "file/name",
        "file/mimetype",
        # "file/source"
    ],
)
def case_suppdocs_empty_fields(test_config: str, missing):

    report_id = test_config["report_id"]
    case_ref = test_config["case_ref"]

    endpoint = f"clients/{case_ref}/reports/" f"{report_id}/supportingdocuments"
    url = f"{test_config['url']}/{endpoint}"
    method = "POST"

    payload = copy.deepcopy(default_supdocs_payload)

    if "/" in missing:
        payload["supporting_document"]["data"][missing.split("/")[0]][
            missing.split("/")[1]
        ] = ""
    else:
        payload["supporting_document"]["data"][missing] = ""

    expected_status_code = 400

    return url, method, payload, expected_status_code


@case(id="Bad payload sent to checklist POST endpoint - missing data: {missing}")
@parametrize(
    missing=[
        "attributes/submission_id",
        "file/name",
        "file/mimetype",
        # "file/source"
    ],
)
def case_checklist_missing_fields(test_config: str, missing):

    report_id = test_config["report_id"]
    case_ref = test_config["case_ref"]

    endpoint = f"clients/{case_ref}/reports/" f"{report_id}/checklists"
    url = f"{test_config['url']}/{endpoint}"
    method = "POST"

    payload = copy.deepcopy(default_checklist_payload)

    if "/" in missing:
        del payload["checklist"]["data"][missing.split("/")[0]][missing.split("/")[1]]
    else:
        del payload["checklist"]["data"][missing]

    expected_status_code = 400

    return url, method, payload, expected_status_code


@case(id="Bad payload sent to checklist POST endpoint - empty data: {missing}")
@parametrize(
    missing=[
        "attributes/submission_id",
        "file/name",
        "file/mimetype",
        # "file/source"
    ],
)
def case_checklist_empty_fields(test_config: str, missing):

    report_id = test_config["report_id"]
    case_ref = test_config["case_ref"]

    endpoint = f"clients/{case_ref}/reports/" f"{report_id}/checklists"
    url = f"{test_config['url']}/{endpoint}"
    method = "POST"

    payload = copy.deepcopy(default_checklist_payload)

    if "/" in missing:
        payload["checklist"]["data"][missing.split("/")[0]][missing.split("/")[1]] = ""
    else:
        payload["checklist"]["data"][missing] = ""

    expected_status_code = 400

    return url, method, payload, expected_status_code


@case(id="Bad payload sent to checklist PUT endpoint - missing data: {missing}")
@parametrize(
    missing=[
        "attributes/submission_id",
        "file/name",
        "file/mimetype",
        # "file/source"
    ],
)
def case_checklist_update_missing_fields(test_config: str, missing):

    report_id = test_config["report_id"]
    case_ref = test_config["case_ref"]
    checklist_id = test_config["checklist_id"]

    endpoint = (
        f"clients/{case_ref}/reports/" f"{report_id}/checklists/" f"{checklist_id}"
    )
    url = f"{test_config['url']}/{endpoint}"
    method = "PUT"

    payload = copy.deepcopy(default_checklist_payload)

    if "/" in missing:
        del payload["checklist"]["data"][missing.split("/")[0]][missing.split("/")[1]]
    else:
        del payload["checklist"]["data"][missing]

    expected_status_code = 400

    return url, method, payload, expected_status_code


@case(id="Bad payload sent to checklist PUT endpoint - empty data: {missing}")
@parametrize(
    missing=[
        "attributes/submission_id",
        "file/name",
        "file/mimetype",
        # "file/source"
    ],
)
def case_checklist_update_empty_fields(test_config: str, missing):

    report_id = test_config["report_id"]
    case_ref = test_config["case_ref"]
    checklist_id = test_config["checklist_id"]

    endpoint = (
        f"clients/{case_ref}/reports/" f"{report_id}/checklists/" f"{checklist_id}"
    )
    url = f"{test_config['url']}/{endpoint}"
    method = "PUT"

    payload = copy.deepcopy(default_checklist_payload)

    if "/" in missing:
        payload["checklist"]["data"][missing.split("/")[0]][missing.split("/")[1]] = ""
    else:
        payload["checklist"]["data"][missing] = ""

    expected_status_code = 400

    return url, method, payload, expected_status_code
