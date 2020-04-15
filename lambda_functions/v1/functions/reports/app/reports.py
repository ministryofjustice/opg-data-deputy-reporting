import json
import logging
import os

from .helpers import compare_two_dicts, format_response_message
from .sirius_service import (
    build_sirius_url,
    build_sirius_headers,
    submit_document_to_sirius,
)

logger = logging.getLogger()

try:
    logger.setLevel(os.environ["LOGGER_LEVEL"])
except KeyError:
    logger.setLevel("INFO")

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("[%(levelname)s] [in %(funcName)s:%(lineno)d] %(message)s")
)
logger.addHandler(handler)


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
        sirius_api_url = build_sirius_url(
            base_url=os.environ["SIRIUS_BASE_URL"],
            api_route=os.environ["SIRIUS_PUBLIC_API_URL"],
            endpoint="documents",
        )

        sirius_payload = transform_event_to_sirius_request(event=event)
        sirius_headers = build_sirius_headers()

        sirius_reponse = submit_document_to_sirius(
            url=sirius_api_url, data=sirius_payload, headers=sirius_headers
        )

        lambda_response = format_response_message(
            json.loads(sirius_reponse["body"])["uuid"],
            event["pathParameters"]["caseref"],
            "reports",
            # submission_id should come from sirius but it's not there atm so faking it
            json.loads(event["body"])["report"]["data"]["attributes"]["submission_id"],
        )
    else:
        lambda_response = {
            "isBase64Encoded": False,
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": f"unable to parse {', '.join(errors)}",
        }

    logger.debug(f"Lambda Response: {lambda_response}")

    print(lambda_response)
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
        "report": {
            "data": {
                "type": "string",
                "attributes": {"submission_id": 1},
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


def transform_event_to_sirius_request(event):
    """
    Takes the 'body' from the AWS event and converts it into the right format for the
    Sirius documents endpoint, detailed here:
    tests/test_data/sirius_documents_payload_schema.json

    Args:
        event: json received from API Gateway
    Returns:
        Sirius-style payload, json
    """

    case_ref = event["pathParameters"]["caseref"]
    request_body = json.loads(event["body"])
    metadata = request_body["report"]["data"]["attributes"]
    file_name = request_body["report"]["data"]["file"]["name"]
    file_type = request_body["report"]["data"]["file"]["mimetype"]
    file_source = request_body["report"]["data"]["file"]["source"]

    payload = {
        "type": "Report - General",
        "caseRecNumber": case_ref,
        "metadata": metadata,
        "file": {"name": file_name, "source": file_source, "type": file_type},
    }
    logger.debug(f"Sirius Payload: {payload}")

    return json.dumps(payload)
