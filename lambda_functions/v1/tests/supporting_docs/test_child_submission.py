from pytest_cases import (
    cases_data,
    CaseDataGetter,
)

from lambda_functions.v1.functions.supporting_docs.app.supporting_docs import (
    is_child_event,
)
from lambda_functions.v1.tests.supporting_docs import child_submission_test_cases


@cases_data(module=child_submission_test_cases)
def test_is_child_submission(case_data: CaseDataGetter):
    child_count, parent_id, sibling_parent_id, expected_result = case_data.get()

    result = is_child_event(child_count, parent_id, sibling_parent_id)

    assert result == expected_result
