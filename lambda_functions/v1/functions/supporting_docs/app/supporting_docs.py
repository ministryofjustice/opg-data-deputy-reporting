import json
import os

from . import sirius_service
from .helpers import compare_two_dicts, custom_logger
from .sirius_service import (
    build_sirius_url,
    submit_document_to_sirius,
)

logger = custom_logger("supporting_docs")


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

        parent_id = determine_document_parent_id(
            url=transform_event_to_sirius_get_url(event)
        )

        sirius_payload = transform_event_to_sirius_post_request(
            event=event, parent_id=parent_id
        )

        sirius_api_url = build_sirius_url(
            base_url=f'{os.environ["SIRIUS_BASE_URL"]}/api/public',
            version=os.environ["API_VERSION"],
            endpoint="documents",
        )

        sirius_response = submit_document_to_sirius(
            url=sirius_api_url, data=sirius_payload
        )

        lambda_response = {
            "isBase64Encoded": False,
            "statusCode": 201,
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


def transform_event_to_sirius_get_url(event):
    case_ref = event["pathParameters"]["caseref"]
    report_id = event["pathParameters"]["id"]
    request_body = json.loads(event["body"])
    submission_id = request_body["supporting_document"]["data"]["attributes"][
        "submission_id"
    ]

    url = build_sirius_url(
        base_url=f'{os.environ["SIRIUS_BASE_URL"]}/api/public',
        version=os.environ["API_VERSION"],
        endpoint=f"documents",
        url_params={
            "caserecnumber": case_ref,
            "metadata[submission_id]": submission_id,
            "metadata[report_id]": report_id,
        },
    )

    return url


def transform_event_to_sirius_post_request(event, parent_id=None):
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

    if parent_id:
        payload["parentUuid"] = parent_id

    logger.debug(f"Sirius Payload: {payload}")

    return json.dumps(payload)


def determine_document_parent_id(url):

    parent_id = None

    submission_entries = sirius_service.send_get_to_sirius(url)

    if submission_entries is not None:

        try:
            number_of_entries = len(
                [entry for entry in submission_entries if len(entry) > 0]
            )

            print(f"number_of_entries: {number_of_entries}")

            if number_of_entries == 0:
                parent_id = None
            else:
                for entry in submission_entries:
                    if "parentUuid" in entry and entry["parentUuid"] is None:
                        parent_id = entry["uuid"]
                        break
                    elif "parentUuid" not in entry:
                        parent_id = entry["uuid"]
                        break
                    else:
                        logger.info("Unable to determine parent id of document")
                        parent_id = None

        except TypeError as e:
            logger.info(f"Unable to determine parent id of document {e}")
            parent_id = None

    return parent_id
