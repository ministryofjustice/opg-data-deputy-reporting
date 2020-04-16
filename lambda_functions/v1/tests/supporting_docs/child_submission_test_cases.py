import copy

from pytest_cases import CaseData

default_parent_id = "9725203f-8c97-4c82-8a18-ea2b88fa7a44"
default_sibling_id = "beac0657-63b7-496b-adea-951a4f2b1956"

default_payload = {"id": "6bac57c3-9f7f-4ea3-97ec-fdaa08efd0f5", "parent_id": ""}


def case_child_count_is_zero() -> CaseData:

    child_count = 0
    parent_id = default_parent_id
    expected_result = copy.deepcopy(default_payload)

    expected_result.pop("parent_id")

    return child_count, parent_id, expected_result


def case_child_count_is_one() -> CaseData:

    child_count = 1
    parent_id = default_parent_id
    expected_result = copy.deepcopy(default_payload)

    expected_result["parent_id"] = parent_id

    return child_count, parent_id, expected_result


def case_child_count_is_many() -> CaseData:

    child_count = 1
    parent_id = default_parent_id
    sibling_id = default_sibling_id
    expected_result = copy.deepcopy(default_payload)

    expected_result["parent_id"] = sibling_id

    return child_count, parent_id, expected_result
