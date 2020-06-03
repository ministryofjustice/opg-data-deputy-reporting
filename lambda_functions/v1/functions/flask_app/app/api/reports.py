import json
import os


from .helpers import custom_logger, compare_two_dicts
from . import sirius_service

logger = custom_logger("reports")


def endpoint_handler(data, caseref):

    try:
        SIRIUS_BASE_URL = os.environ["SIRIUS_BASE_URL"]
        API_VERSION = os.environ["API_VERSION"]
    except KeyError as e:
        logger.error(f"{e} not set")
        return "internal server error", 500

    valid_payload, errors = validate_payload_data(data=data)

    if valid_payload:

        sirius_api_url = sirius_service.build_sirius_url(
            base_url=f"{SIRIUS_BASE_URL}/api/public",
            version=API_VERSION,
            endpoint="documents",
        )
        print(f"sirius_api_url: {sirius_api_url}")

        sirius_payload = transform_payload_data_to_sirius_request(
            data=data, caseref=caseref
        )
        print(f"sirius_payload: {sirius_payload}")

        sirius_headers = sirius_service.build_sirius_headers()
        print(f"sirius_headers: {sirius_headers}")

        try:
            (
                sirius_response_code,
                sirius_response,
            ) = sirius_service.submit_document_to_sirius(
                url=sirius_api_url, data=sirius_payload, headers=sirius_headers
            )
            print(f"sirius_response: {sirius_response}")
        except Exception as e:
            print(f"e: {e}")

        return (json.dumps(sirius_response), sirius_response_code)
    else:
        return "unable to parse payload", 400


def validate_payload_data(data):
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
    print(f"json_data: {data}")

    errors = compare_two_dicts(required_body_structure, data, missing=[])

    print(f"errors: {errors}")

    if len(errors) > 0:
        logger.debug(f"Validation failed: {', '.join(errors)}")
        return False, errors
    else:
        logger.debug("Validation passed")
        return True, errors


def transform_payload_data_to_sirius_request(data, caseref=None):
    case_ref = caseref
    # request_body = json.loads(json_data)
    print(f"type(json_data): {type(data)}")
    request_body = data

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
