import json

from lambda_functions.supporting_docs.supporting_docs import lambda_handler, \
    transform_event_to_sirius_request
from tests.helpers.use_test_data import is_valid_schema, load_data


def test_lambda_handler(patched_requests, patched_get_secret_supporting_docs):
    event = load_data("supporting_docs_event.json", as_json=False)
    context = None

    result = lambda_handler(event=event, context=context)

    assert is_valid_schema(json.dumps(result), "standard_lambda_response.json")



def test_transform_event_to_sirius_request():
    event = load_data("supporting_docs_event.json", as_json=False)

    payload = transform_event_to_sirius_request(event)

    assert is_valid_schema(json.loads(payload), "sirius_documents_payload.json")
