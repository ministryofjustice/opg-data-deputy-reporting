import json

from . import sirius_service
from .helpers import custom_logger

logger = custom_logger("checklists")


def endpoint_handler(data, caseref, id, checklist_id, method):

    endpoint = transform_payload_to_endpoint(checklist_id=checklist_id)

    sirius_payload = transform_payload_to_sirius_post_request(
        data=data, caseref=caseref, id=id
    )

    api_status_code, api_response = sirius_service.new_submit_document_to_sirius(
        data=sirius_payload, endpoint=endpoint, method=method
    )

    try:
        api_response["data"]["type"] = "checklists"
    except (KeyError, TypeError):
        pass
    return api_response, api_status_code


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
