import json
import os
import copy

from .helpers import compare_two_dicts, custom_logger
from .sirius_service import (
    build_sirius_url,
    submit_document_to_sirius,
    build_sirius_headers,
)

logger = custom_logger("checklists")


def lambda_handler(event, context):
    """

    Args:
        event: json received from API Gateway
        context:
    Returns:
        Response from Sirius in AWS Lambda format, json
    """

    valid_payload, errors = validate_event(event=event)

    if valid_payload:

        sirius_payload = transform_event_to_sirius_payload(event=event)
        sirius_headers = build_sirius_headers()

        sirius_api_url = build_sirius_url(
            base_url=f'{os.environ["SIRIUS_BASE_URL"]}/api/public',
            version=os.environ["API_VERSION"],
            endpoint=transform_event_to_endpoint(event),
        )

        sirius_response_code, sirius_response = submit_document_to_sirius(
            method=event["httpMethod"],
            url=sirius_api_url,
            data=sirius_payload,
            headers=sirius_headers,
        )

        try:
            sirius_response["data"]["type"] = "checklists"
        except (KeyError, TypeError):
            pass

        lambda_response = {
            "isBase64Encoded": False,
            "statusCode": sirius_response_code,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(sirius_response),
        }
    else:
        lambda_response = {
            "isBase64Encoded": False,
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": f"unable to parse {', '.join(errors)}",
        }
    logger.debug(f"Lambda Response: {lambda_response}")

    return lambda_response


def validate_event(event):
    """
    The request body *should* be validated by API-G before it gets this far,
    but given everything blows up if any of these required fields are missing/wrong
    then it's worth double checking here, and providing integrators with a meaningful
    error message

    Args:
        event: AWS event json

    Returns:
        tuple: valid boolean, error list
    """

    required_body_structure = {
        "checklist": {
            "data": {
                "attributes": {"submission_id": 0},
                "file": {"name": "string", "mimetype": "string", "source": "string"},
            }
        }
    }

    errors = compare_two_dicts(
        required_body_structure, json.loads(event["body"]), missing=[]
    )

    if len(errors) > 0:
        return False, errors
    else:
        return True, errors


def transform_event_to_endpoint(event):
    """
    In the case of a PUT request, pass the checklist uuid through

    Args:
        event: AWS event json

    Returns:
        string: endpoint

    """
    if "PUT" == event["httpMethod"]:
        endpoint = f'documents/{event["pathParameters"]["checklistId"]}'
    else:
        endpoint = "documents"

    return endpoint


def transform_event_to_sirius_payload(event):
    """
    Takes the 'body' from the AWS event and converts it into the right format for the
    Sirius documents endpoint, detailed here:
    tests/test_data/sirius_documents_payload_schema.json

    Args:
        event: json received from API Gateway
    Returns:
        Sirius-style payload, json
    """
    report_id = event["pathParameters"]["id"]
    case_ref = event["pathParameters"]["caseref"]
    request_body = json.loads(event["body"])
    metadata = request_body["checklist"]["data"]["attributes"]
    metadata["report_id"] = report_id
    metadata["is_checklist"] = "true"
    file_name = request_body["checklist"]["data"]["file"]["name"]
    file_type = request_body["checklist"]["data"]["file"]["mimetype"]
    file_source = request_body["checklist"]["data"]["file"]["source"]

    payload = {
        "type": "Report - Checklist",
        "caseRecNumber": case_ref,
        "metadata": metadata,
        "file": {"name": file_name, "source": file_source, "type": file_type},
    }

    debug_payload = copy.deepcopy(payload)
    debug_payload["file"]["source"] = "REDACTED"
    logger.debug(f"Sirius Payload: {debug_payload}")

    return json.dumps(payload)
