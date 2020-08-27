import json
import copy

from . import sirius_service
from .helpers import custom_logger, handle_file_source

logger = custom_logger("reports")


def endpoint_handler(data, caseref):
    sirius_payload, s3_error = transform_payload_data_to_sirius_request(
        data=data, caseref=caseref
    )

    if s3_error is None:
        api_status_code, api_response = sirius_service.new_submit_document_to_sirius(
            data=sirius_payload
        )
    elif s3_error == "ACCESS_ERROR":
        api_response = sirius_service.handle_sirius_error(
            error_code=404,
            error_message="404 Not found: s3 error",
            error_details="s3 object not accessible",
        )
        api_status_code = 404
    elif s3_error == "READ_ERROR":
        api_response = sirius_service.handle_sirius_error(
            error_code=400,
            error_message="400 Bad Request: s3 error",
            error_details="s3 object not readable",
        )
        api_status_code = 400
    else:
        pass
    try:
        api_response["data"]["type"] = "reports"
    except (KeyError, TypeError):
        pass

    return api_response, api_status_code


def transform_payload_data_to_sirius_request(data, caseref=None):
    case_ref = caseref

    request_body = data

    metadata = request_body["report"]["data"]["attributes"]
    file_name = request_body["report"]["data"]["file"]["name"]
    file_type = request_body["report"]["data"]["file"]["mimetype"]
    file_source, err = handle_file_source(file=request_body["report"]["data"]["file"])

    payload = {
        "type": "Report",
        "caseRecNumber": case_ref,
        "metadata": metadata,
        "file": {"name": file_name, "source": file_source, "type": file_type},
    }

    debug_payload = copy.deepcopy(payload)
    debug_payload["file"]["source"] = "REDACTED"
    logger.debug(f"Sirius Payload: {debug_payload}")

    return json.dumps(payload), err
