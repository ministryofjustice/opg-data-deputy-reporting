import json
import logging
import os

from .helpers import compare_two_dicts
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

        # submission_id should come from sirius but it's not there atm so faking it
        lambda_response_body = {
            "data": {
                "type": "supporting_document",
                "id": json.loads(sirius_reponse["body"])["uuid"],
                "attributes": {
                    "submission_id": json.loads(event["body"])["supporting_document"][
                        "data"
                    ]["attributes"]["submission_id"]
                },
            }
        }

        lambda_response = {
            "isBase64Encoded": False,
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(lambda_response_body),
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
        "supporting_document": {
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
    report_id = event["pathParameters"]["id"]
    case_ref = event["pathParameters"]["caseref"]
    request_body = json.loads(event["body"])
    metadata = request_body["supporting_document"]["data"]["attributes"]
    metadata["report_id"] = report_id
    file_name = request_body["supporting_document"]["data"]["file"]["name"]
    file_type = request_body["supporting_document"]["data"]["file"]["mimetype"]
    file_source = request_body["supporting_document"]["data"]["file"]["source"]

    payload = {
        "type": "Report",
        "caseRecNumber": case_ref,
        "metadata": metadata,
        "file": {"name": file_name, "source": file_source, "type": file_type},
    }
    logger.debug(f"Sirius Payload: {payload}")

    return json.dumps(payload)


def is_child_event():
    pass
