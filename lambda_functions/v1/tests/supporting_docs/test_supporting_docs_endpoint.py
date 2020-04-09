import json

from lambda_functions.v1.functions.supporting_docs.app.supporting_docs import (
    lambda_handler,
    transform_event_to_sirius_request,
    validate_event,
)
from lambda_functions.v1.tests.helpers.use_test_data import (
    is_valid_schema,
    load_data,
    build_aws_event,
)

from pytest_cases import (
    cases_data,
    CaseDataGetter,
)

from lambda_functions.v1.tests.supporting_docs import (
    supporting_docs_endpoint_test_cases,
)


def test_lambda_handler(patched_requests, patched_get_secret):
    event = load_data("supporting_docs_event.json", as_json=False)
    context = None

    result = lambda_handler(event=event, context=context)
    assert is_valid_schema(json.dumps(result), "standard_lambda_response_schema.json")


@cases_data(module=supporting_docs_endpoint_test_cases)
def test_validate_payload(case_data: CaseDataGetter):
    body, case_ref, report_id, expected_result = case_data.get()
    path_params = {"caseref": case_ref, "id": report_id}
    event = build_aws_event(
        event_body=json.dumps(body), event_path_parementers=path_params, as_json=False
    )

    valid_event, errors = validate_event(event)

    print(valid_event)
    print(errors)

    assert valid_event == expected_result[0]
    assert sorted(errors) == sorted(expected_result[1])


def test_transform_event_to_sirius_request(
    default_supporting_doc_request_body,
    default_request_case_ref,
    default_request_report_id,
    default_sirius_supporting_docs_request,
):

    path_params = {"caseref": default_request_case_ref, "id": default_request_report_id}
    event = build_aws_event(
        event_body=json.dumps(default_supporting_doc_request_body),
        event_path_parementers=path_params,
        as_json=False,
    )

    payload = transform_event_to_sirius_request(event)

    assert is_valid_schema(json.loads(payload), "sirius_documents_payload_schema.json")
    assert payload == json.dumps(default_sirius_supporting_docs_request)


def test_sirius_request_has_submission_id(
    default_supporting_doc_request_body,
    default_request_case_ref,
    default_request_report_id,
    default_sirius_supporting_docs_request,
):

    path_params = {"caseref": default_request_case_ref, "id": default_request_report_id}
    event = build_aws_event(
        event_body=json.dumps(default_supporting_doc_request_body),
        event_path_parementers=path_params,
        as_json=False,
    )

    payload = transform_event_to_sirius_request(event)

    assert json.loads(payload)["metadata"]["submission_id"]


def test_sirius_request_has_report_id_from_path(
    default_supporting_doc_request_body,
    default_request_case_ref,
    default_request_report_id,
    default_sirius_supporting_docs_request,
):
    default_supporting_doc_request_body["supporting_document"]["data"]["attributes"][
        "report_id"
    ] = "uuid_from_attributes"
    path_params = {"caseref": default_request_case_ref, "id": "uuid_from_path"}
    event = build_aws_event(
        event_body=json.dumps(default_supporting_doc_request_body),
        event_path_parementers=path_params,
        as_json=False,
    )

    payload = transform_event_to_sirius_request(event)

    assert json.loads(payload)["metadata"]["report_id"] == "uuid_from_path"
