import json

from pytest_cases import (
    cases_data,
    CaseDataGetter,
)

from lambda_functions.v1.functions.checklists.app.checklists import (
    lambda_handler,
    transform_event_to_sirius_payload,
    validate_event,
)
from lambda_functions.v1.tests.helpers.use_test_data import (
    is_valid_schema,
    load_data,
    build_aws_event,
)
from lambda_functions.v1.tests.checklists import (
    checklists_endpoint_test_cases,
)


def test_lambda_handler(
    patched_requests, patched_get_secret, patched_validate_event_success
):
    event = load_data("checklists_event.json", as_json=False)
    context = None

    result = lambda_handler(event=event, context=context)
    assert result["statusCode"] == 201
    assert is_valid_schema(result, "standard_lambda_response_schema.json")
    assert is_valid_schema(json.loads(result["body"]), "201_created_schema.json")


def test_lambda_handler_fail(
    patched_requests, patched_get_secret, patched_validate_event_fail
):
    event = load_data("checklists_event.json", as_json=False)
    context = None

    result = lambda_handler(event=event, context=context)
    assert result["statusCode"] == 400
    assert is_valid_schema(result, "standard_lambda_response_schema.json")


@cases_data(module=checklists_endpoint_test_cases)
def test_validate_event(case_data: CaseDataGetter):
    body, case_ref, report_id, expected_result = case_data.get()
    path_params = {"caseref": case_ref, "id": report_id}
    event = build_aws_event(
        event_body=json.dumps(body), event_path_parementers=path_params, as_json=False
    )

    valid_event, errors = validate_event(event)

    assert valid_event == expected_result[0]
    assert sorted(errors) == sorted(expected_result[1])


def test_transform_event_to_sirius_request(
    default_checklists_request_body,
    default_request_case_ref,
    default_request_report_id,
    default_sirius_checklists_request
):
    path_params = {"caseref": default_request_case_ref, "id": default_request_report_id}
    event = build_aws_event(
        event_body=json.dumps(default_checklists_request_body),
        event_path_parementers=path_params,
        as_json=False,
    )

    payload = transform_event_to_sirius_payload(event)

    assert is_valid_schema(json.loads(payload), "sirius_documents_payload_schema.json")
    assert payload == json.dumps(default_sirius_checklists_request)


def test_transform_event_to_sirius_request_with_no_report_submission(
    default_request_case_ref,
    nondigital_request_report_id,
    checklists_request_body_with_no_report_submission,
    sirius_checklists_request_with_no_report_submission
):
    path_params = {"caseref": default_request_case_ref, "id": nondigital_request_report_id}
    event = build_aws_event(
        event_body=json.dumps(checklists_request_body_with_no_report_submission),
        event_path_parementers=path_params,
        as_json=False,
    )

    payload = transform_event_to_sirius_payload(event)

    assert is_valid_schema(json.loads(payload), "sirius_documents_payload_schema.json")
    assert payload == json.dumps(sirius_checklists_request_with_no_report_submission)


def test_sirius_request_has_report_id_from_path(
    default_checklists_request_body,
    default_request_case_ref,
    default_request_report_id,
    default_sirius_checklists_request,
):
    default_checklists_request_body["checklist"]["data"]["attributes"]["report_id"] = "uuid_from_attributes"
    path_params = {"caseref": default_request_case_ref, "id": "uuid_from_path"}
    event = build_aws_event(
        event_body=json.dumps(default_checklists_request_body),
        event_path_parementers=path_params,
        as_json=False,
    )

    payload = transform_event_to_sirius_payload(event)

    assert json.loads(payload)["metadata"]["report_id"] == "uuid_from_path"
