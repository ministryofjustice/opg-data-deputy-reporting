import json
import os

from . import sirius_service
from .helpers import custom_logger

logger = custom_logger("checklists")


def endpoint_handler(data, caseref, id, checklist_id, method):

    try:
        SIRIUS_BASE_URL = os.environ["SIRIUS_BASE_URL"]
        API_VERSION = os.environ["API_VERSION"]
    except KeyError as e:
        logger.error(f"{e} not set")
        return "internal server error", 500

    # valid_payload, errors = validate_payload_data(data=data)
    #
    # if valid_payload:

    sirius_api_url = sirius_service.build_sirius_url(
        base_url=f"{SIRIUS_BASE_URL}/api/public",
        version=API_VERSION,
        endpoint=transform_payload_to_endpoint(checklist_id=checklist_id),
    )

    sirius_payload = transform_payload_to_sirius_post_request(
        data=data, caseref=caseref, id=id
    )

    sirius_headers = sirius_service.build_sirius_headers()

    (sirius_response_code, sirius_response,) = sirius_service.submit_document_to_sirius(
        url=sirius_api_url, data=sirius_payload, headers=sirius_headers, method=method
    )

    return (sirius_response, sirius_response_code)
    # else:
    #     return "unable to parse payload", 400


#
# def validate_payload_data(data):
#
#     required_body_structure = {
#         "checklist": {
#             "data": {
#                 "attributes": {"submission_id": 0},
#                 "file": {"name": "string", "mimetype": "string", "source": "string"},
#             }
#         }
#     }
#
#     errors = compare_two_dicts(required_body_structure, data, missing=[])
#
#     if len(errors) > 0:
#         logger.debug(f"Validation failed: {', '.join(errors)}")
#         return False, errors
#     else:
#         logger.debug("Validation passed")
#         return True, errors


def transform_payload_to_sirius_post_request(
    data, caseref=None, id=None,
):
    report_id = id
    case_ref = caseref
    request_body = data

    metadata = request_body["checklist"]["data"]["attributes"]
    metadata["report_id"] = report_id
    file_name = request_body["checklist"]["data"]["file"]["name"]
    file_type = request_body["checklist"]["data"]["file"]["mimetype"]
    file_source = request_body["checklist"]["data"]["file"]["source"]

    payload = {
        "type": "Report - Checklist",
        "caseRecNumber": case_ref,
        "metadata": metadata,
        "file": {"name": file_name, "source": file_source, "type": file_type},
    }

    logger.debug(f"Sirius Payload: {payload}")

    return json.dumps(payload)


def transform_payload_to_endpoint(checklist_id=None):
    """
    In the case of a PUT request, pass the checklist uuid through

    Args:
        event: AWS event json

    Returns:
        string: endpoint

    """
    if checklist_id:
        endpoint = f"documents/{checklist_id}"
    else:
        endpoint = "documents"

    return endpoint
