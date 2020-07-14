import random

from pytest_cases import CaseData, case_name

from lambda_functions.v1.integration_tests.conftest import generate_file_name

new_submission_id = random.randint(10000, 99999)


@case_name(
    "Successful post to supporting docs endpoint - doc is child of existing "
    "report sent in the same submission"
)
def case_success_original(test_config: str) -> CaseData:

    report_id = test_config["report_id"]
    submission_id = test_config["submission_id"]
    case_ref = test_config["case_ref"]

    endpoint = f"clients/{case_ref}/reports/" f"{report_id}/supportingdocuments"
    url = f"{test_config['url']}/{endpoint}"

    method = "POST"
    payload = {
        "supporting_document": {
            "data": {
                "type": "supportingdocuments",
                "attributes": {"submission_id": submission_id},
                "file": {
                    "name": f"{generate_file_name()}.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }

    # Expected returns

    expected_status_code = 201
    expected_response_data = {
        "type": "supportingdocuments",
        "submission_id": submission_id,
        "parent_id": report_id,
        "report_id": report_id,
    }

    return url, method, payload, expected_status_code, expected_response_data


@case_name(
    "Successful post to supporting docs endpoint - doc is child of existing "
    "report sent in a different submission"
)
def case_success_new_submission(test_config: str) -> CaseData:

    report_id = test_config["report_id"]
    submission_id = 54321
    case_ref = test_config["case_ref"]

    endpoint = f"clients/{case_ref}/reports/" f"{report_id}/supportingdocuments"
    url = f"{test_config['url']}/{endpoint}"

    method = "POST"
    payload = {
        "supporting_document": {
            "data": {
                "type": "supportingdocuments",
                "attributes": {"submission_id": submission_id},
                "file": {
                    "name": f"{generate_file_name()}.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }

    # Expected returns

    expected_status_code = 201
    expected_response_data = {
        "type": "supportingdocuments",
        "submission_id": submission_id,
        "parent_id": None,
        "report_id": report_id,
    }

    return url, method, payload, expected_status_code, expected_response_data


@case_name(
    "Successful post to supporting docs endpoint - doc is child of existing "
    "report sent in a different submission  - set up for the following test"
)
def case_success_new_submission_2(test_config: str) -> CaseData:

    report_id = test_config["report_id"]
    submission_id = 543218
    case_ref = test_config["case_ref"]

    endpoint = f"clients/{case_ref}/reports/" f"{report_id}/supportingdocuments"
    url = f"{test_config['url']}/{endpoint}"

    method = "POST"
    payload = {
        "supporting_document": {
            "data": {
                "type": "supportingdocuments",
                "attributes": {"submission_id": submission_id},
                "file": {
                    "name": f"{generate_file_name()}.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }

    # Expected returns

    expected_status_code = 201
    expected_response_data = {
        "type": "supportingdocuments",
        "submission_id": submission_id,
        # "parent_id": None,
        "report_id": report_id,
    }

    return url, method, payload, expected_status_code, expected_response_data


@case_name(
    "Successful post to supporting docs endpoint - doc is child of existing "
    "supporting doc "
)
def case_success_new_submission_child(test_config: str) -> CaseData:

    report_id = test_config["report_id"]
    submission_id = 543218
    case_ref = test_config["case_ref"]

    parent_id = test_config["supp_doc_id"]

    endpoint = f"clients/{case_ref}/reports/" f"{report_id}/supportingdocuments"
    url = f"{test_config['url']}/{endpoint}"

    method = "POST"
    payload = {
        "supporting_document": {
            "data": {
                "type": "supportingdocuments",
                "attributes": {"submission_id": submission_id},
                "file": {
                    "name": f"{generate_file_name()}.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }

    # Expected returns

    expected_status_code = 201
    expected_response_data = {
        "type": "supportingdocuments",
        "submission_id": submission_id,
        "parent_id": parent_id,
        "report_id": report_id,
    }

    return url, method, payload, expected_status_code, expected_response_data
