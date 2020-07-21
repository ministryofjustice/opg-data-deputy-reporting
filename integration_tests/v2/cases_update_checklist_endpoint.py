import random

import pytest
from pytest_cases import CaseData, cases_generator

from integration_tests.v2.conftest import generate_file_name

new_submission_id = random.randint(10000, 99999)


@pytest.mark.xfail(reason="OpenAPI spec problems")
@cases_generator(
    "Successful multiple updates of a checklist with different "
    "submission_ids: {sub_id}",
    sub_id=[22222, 33333, 44444, 55555],
)
def case_success_original_IN_112(test_config: str, sub_id: int) -> CaseData:

    report_id = test_config["report_id"]
    submission_id = sub_id
    case_ref = test_config["case_ref"]
    checklist_id = test_config["checklist_id"]

    endpoint = (
        f"clients/{case_ref}/reports/" f"{report_id}/checklists/" f"{checklist_id}"
    )
    url = f"{test_config['url']}/{endpoint}"

    method = "PUT"
    payload = {
        "checklist": {
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

    expected_status_code = 200
    expected_response_data = {
        "type": "checklists",
        "submission_id": submission_id,
        "original_checklist_id": checklist_id,
    }

    return url, method, payload, expected_status_code, expected_response_data
