from pytest_cases import case_name, CaseData


@case_name("Successful post to supporting docs endpoint")
def case_success() -> CaseData:

    test_data = {
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
    }
    test_case_ref = 1111
    test_report_id = "de26f80c-ed6d-4c52-b6bd-e0260bb0faf0"

    test_headers = {"Content-Type": "application/json"}

    expected_response_status_code = 201
    expected_response_data = {
        "data": {
            "attributes": {"submission_id": 12345, "parent_id": None},
            "id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            "type": "Report - General",
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
