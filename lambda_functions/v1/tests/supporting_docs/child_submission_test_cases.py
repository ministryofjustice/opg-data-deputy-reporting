def case_first_document_in_submission():
    report_get_response = [{}]
    parent_id = None
    expected_result = parent_id

    return report_get_response, expected_result


def case_second_document_in_submission():
    report_get_response = [
        {"uuid": "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0", "parentUuid": None}
    ]
    parent_id = "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0"
    expected_result = parent_id

    return report_get_response, expected_result


def case_fifth_document_in_submission():
    report_get_response = [
        {"uuid": "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0", "parentUuid": None},
        {
            "uuid": "772a922c-2372-4bf4-8040-cb0bf4fb7ccf",
            "parentUuid": "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0",
        },
        {
            "uuid": "b9d242a2-6a4f-4f1e-9642-07cb18d36945",
            "parentUuid": "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0",
        },
        {
            "uuid": "168fb7de-e982-4bf4-a820-751ea529c5fc",
            "parentUuid": "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0",
        },
    ]
    parent_id = "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0"
    expected_result = parent_id

    return report_get_response, expected_result


def case_parentuuid_does_not_exist():
    report_get_response = [{"uuid": "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0"}]
    parent_id = "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0"
    expected_result = parent_id

    return report_get_response, expected_result


def case_too_many_parent_ids():
    report_get_response = [
        {"uuid": "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0", "parentUuid": None},
        {"uuid": "772a922c-2372-4bf4-8040-cb0bf4fb7ccf", "parentUuid": None},
        {"uuid": "b9d242a2-6a4f-4f1e-9642-07cb18d36945", "parentUuid": None},
        {"uuid": "168fb7de-e982-4bf4-a820-751ea529c5fc", "parentUuid": None},
    ]
    first_parent_id = "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0"
    expected_result = first_parent_id

    return report_get_response, expected_result


def case_response_is_all_wrong():
    report_get_response = "this is all wrong"
    parent_id = None
    expected_result = parent_id

    return report_get_response, expected_result
