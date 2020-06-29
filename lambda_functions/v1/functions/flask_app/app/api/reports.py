import json
import os

from . import sirius_service
from .helpers import custom_logger

logger = custom_logger("reports")


def endpoint_handler(data, caseref):

    try:
        SIRIUS_BASE_URL = os.environ["SIRIUS_BASE_URL"]
        API_VERSION = os.environ["API_VERSION"]
    except KeyError as e:
        logger.error(f"{e} not set")
        return "internal server error", 500

    sirius_api_url = sirius_service.build_sirius_url(
        base_url=f"{SIRIUS_BASE_URL}/api/public",
        version=API_VERSION,
        endpoint="documents",
    )
    print(f"sirius_api_url: {sirius_api_url}")

    sirius_payload = transform_payload_data_to_sirius_request(
        data=data, caseref=caseref
    )

    sirius_headers = sirius_service.build_sirius_headers()

    try:
        (
            sirius_response_code,
            sirius_response,
        ) = sirius_service.submit_document_to_sirius(
            url=sirius_api_url, data=sirius_payload, headers=sirius_headers
        )

    except Exception as e:
        logger.error(f"Error sending document to Sirius: {e}")

    return (sirius_response, sirius_response_code)


def transform_payload_data_to_sirius_request(data, caseref=None):
    case_ref = caseref
    # request_body = json.loads(json_data)

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
