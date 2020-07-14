from pytest_cases import case_name, CaseData


@case_name("Successful post to checklist endpoint")
def case_success() -> CaseData:

    test_data = {
        "checklist": {
            "data": {
                "type": "checklists",
                "attributes": {"submission_id": 12345},
                "file": {
                    "name": "Checklist.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }
    test_case_ref = 1111
    test_report_id = "de26f80c-ed6d-4c52-b6bd-e0260bb0faf0"

    test_headers = {"Content-Type": "application/json"}

    expected_response_status_code = 201
    expected_response_data = {
        "data": {
            "attributes": {"parent_id": None, "submission_id": 12345},
            "id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            # "type": "Report - Checklist",
            "type": "checklists",
        }
    }

    return (
        test_data,
        test_headers,
        test_report_id,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
    )


@case_name("Successful post to checklist endpoint no submission id")
def case_success_no_submission_id() -> CaseData:

    test_data = {
        "checklist": {
            "data": {
                "type": "checklists",
                "attributes": {},
                "file": {
                    "name": "Checklist.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }
    test_case_ref = 1111
    test_report_id = "99999999-9999-9999-9999-999999999999"

    test_headers = {"Content-Type": "application/json"}

    expected_response_status_code = 201
    expected_response_data = {
        "data": {
            "attributes": {"parent_id": None, "submission_id": None},
            "id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            "type": "Report - Checklist",
        }
    }

    return (
        test_data,
        test_headers,
        test_report_id,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
    )