import json

from lambda_functions.v1.functions.reports.reports import (
    lambda_handler,
    transform_event_to_sirius_request,
)
from lambda_functions.v1.tests.helpers.use_test_data import is_valid_schema, load_data


def test_lambda_handler(patched_requests, patched_get_secret):
    event = load_data("lambda_event.json", as_json=False)
    context = None

    result = lambda_handler(event=event, context=context)

    assert is_valid_schema(json.dumps(result), "lambda_response.json")


def test_transform_event_to_sirius_request():
    event = load_data("lambda_event.json", as_json=False)

    payload = transform_event_to_sirius_request(event)

    assert is_valid_schema(json.loads(payload), "sirius_documents_payload.json")