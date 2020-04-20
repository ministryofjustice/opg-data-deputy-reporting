from pytest_cases import (
    cases_data,
    CaseDataGetter,
)

from lambda_functions.v1.functions.supporting_docs.app.supporting_docs import (
    determine_document_parent_id,
)
from lambda_functions.v1.tests.supporting_docs import child_submission_test_cases


@cases_data(module=child_submission_test_cases)
def test_is_child_submission(case_data: CaseDataGetter):
    report_get_response, expected_result = case_data.get()

    print(report_get_response)
    result = determine_document_parent_id(report_get_response)

    assert result == expected_result
