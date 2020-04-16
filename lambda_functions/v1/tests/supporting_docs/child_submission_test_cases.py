from pytest_cases import CaseData

default_parent_id = "9725203f-8c97-4c82-8a18-ea2b88fa7a44"
default_sibling_parent_id = "beac0657-63b7-496b-adea-951a4f2b1956"


def case_child_count_is_zero() -> CaseData:

    child_count = 0
    parent_id = None
    sibling_parent_id = None
    expected_result = None

    return child_count, parent_id, sibling_parent_id, expected_result


def case_child_count_is_one() -> CaseData:

    child_count = 1
    parent_id = default_parent_id
    sibling_parent_id = None
    expected_result = parent_id

    return child_count, parent_id, sibling_parent_id, expected_result


def case_child_count_is_many() -> CaseData:

    child_count = 6
    parent_id = default_parent_id
    sibling_parent_id = default_sibling_parent_id
    expected_result = sibling_parent_id

    return child_count, parent_id, sibling_parent_id, expected_result
