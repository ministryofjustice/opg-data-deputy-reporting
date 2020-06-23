import json
import os

from . import sirius_service
from .helpers import custom_logger

logger = custom_logger("supporting_docs")


def endpoint_handler(data, caseref, id):

    try:
        SIRIUS_BASE_URL = os.environ["SIRIUS_BASE_URL"]
        API_VERSION = os.environ["API_VERSION"]
    except KeyError as e:
        logger.error(f"{e} not set")
        return "internal server error", 500

    # valid_payload, errors = validate_payload_data(data=data)

    # if valid_payload:

    sirius_api_url = sirius_service.build_sirius_url(
        base_url=f"{SIRIUS_BASE_URL}/api/public",
        version=API_VERSION,
        endpoint="documents",
    )

    parent_id = determine_document_parent_id(data=data, case_ref=caseref, report_id=id)

    sirius_payload = transform_payload_to_sirius_post_request(
        data=data, caseref=caseref, id=id, parent_id=parent_id
    )

    sirius_headers = sirius_service.build_sirius_headers()

    (sirius_response_code, sirius_response,) = sirius_service.submit_document_to_sirius(
        url=sirius_api_url, data=sirius_payload, headers=sirius_headers
    )

    return (sirius_response, sirius_response_code)
    # else:
    #     return "unable to parse payload", 400


def transform_payload_to_sirius_post_request(
    data, caseref=None, id=None, parent_id=None
):
    report_id = id
    case_ref = caseref
    request_body = data

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


def transform_payload_to_sirius_get_url(data, case_ref, report_id):

    request_body = data

    submission_id = request_body["supporting_document"]["data"]["attributes"][
        "submission_id"
    ]

    url = sirius_service.build_sirius_url(
        base_url=f'{os.environ["SIRIUS_BASE_URL"]}/api/public',
        version=os.environ["API_VERSION"],
        endpoint="documents",
        url_params={
            "caserecnumber": case_ref,
            "metadata[submission_id]": submission_id,
            "metadata[report_id]": report_id,
        },
    )

    return url


def determine_document_parent_id(data, case_ref, report_id):

    url = transform_payload_to_sirius_get_url(data, case_ref, report_id)

    parent_id = None

    submission_entries = sirius_service.send_get_to_sirius(url)

    if submission_entries is not None:

        try:
            number_of_entries = len(
                [entry for entry in submission_entries if len(entry) > 0]
            )

            if number_of_entries == 0:
                parent_id = None
            else:
                for entry in submission_entries:

                    if "parentUuid" in entry and entry["parentUuid"] is None:
                        parent_id = entry["uuid"]
                        break
                    elif "parentUuid" not in entry:
                        # parent_id = entry["uuid"]
                        parent_id = None
                        break
                    else:
                        logger.info("Unable to determine parent id of document")
                        parent_id = None

        except TypeError as e:
            logger.info(f"Unable to determine parent id of document {e}")
            parent_id = None

    return parent_id


# def validate_payload_data(data):
#
#     required_body_structure = {
#         "supporting_document": {
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
