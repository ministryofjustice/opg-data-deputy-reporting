import json

from . import sirius_service
from .helpers import custom_logger

logger = custom_logger("reports")


def endpoint_handler(data, caseref):

    sirius_payload = transform_payload_data_to_sirius_request(
        data=data, caseref=caseref
    )

    api_status_code, api_response = sirius_service.new_submit_document_to_sirius(
        data=sirius_payload
    )

    try:
        api_response["data"]["type"] = "reports"
    except KeyError:
        pass

    return api_response, api_status_code


def transform_payload_data_to_sirius_request(data, caseref=None):
    case_ref = caseref

    request_body = data

    metadata = request_body["report"]["data"]["attributes"]
    file_name = request_body["report"]["data"]["file"]["name"]
    file_type = request_body["report"]["data"]["file"]["mimetype"]
    file_source = request_body["report"]["data"]["file"]["source"]

    payload = {
        "type": "Report",
        "caseRecNumber": case_ref,
        "metadata": metadata,
        "file": {"name": file_name, "source": file_source, "type": file_type},
    }
    logger.debug(f"Sirius Payload: {payload}")

    return json.dumps(payload)
