import json
import pytest

from lambda_functions.v1.functions.reports.reports import (
    lambda_handler,
    transform_event_to_sirius_request,
)
from lambda_functions.v1.tests.helpers.use_test_data import (
    is_valid_schema,
    load_data,
    build_aws_event,
)
from pytest_cases import (
    cases_data,
    CaseDataGetter,
    unfold_expected_err,
    CaseData,
    THIS_MODULE,
)

from lambda_functions.v1.tests.sirius_documents import reports_endpoint_data


def test_lambda_handler(patched_requests, patched_get_secret):
    event = load_data("standard_lambda_event.json", as_json=False)

    context = None

    result = lambda_handler(event=event, context=context)

    assert is_valid_schema(json.dumps(result), "standard_lambda_response.json")


@cases_data(module=reports_endpoint_data)
def test_transform_event_to_sirius_request_2(case_data: CaseDataGetter):
    body, case_ref, expected_result = case_data.get()
    path_params = {"caseref": case_ref}
    event = build_aws_event(
        event_body=json.dumps(body), event_path_parementers=path_params, as_json=False
    )

    payload = transform_event_to_sirius_request(event)

    assert is_valid_schema(json.loads(payload), "sirius_documents_payload.json")
    assert payload == json.dumps(expected_result)
