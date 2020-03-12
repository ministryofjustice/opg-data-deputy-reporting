import json
import logging
import os

import requests


def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(os.environ["LOGGER_LEVEL"])

    sirius_payload = transform_event_to_sirius_request(event)

    sirius_response = submit_document_to_sirius(sirius_payload, None)

    return json.dumps(sirius_response)


# Sirius API Service


def transform_event_to_sirius_request(event):
    request_body = event
    case_ref = request_body["pathParameters"]["caseref"]

    file = json.loads(request_body["body"])["file"]
    file_name = file["fileName"]
    source = file["source"]

    payload = {
        "caseRef": case_ref,
        "direction": "DIRECTION_INCOMING",
        "documentSubType": "Report - General",
        "documentType": "Report - General",
        "file": {
            "fileName": file_name,
            "mimeType": "application/pdf",
            "source": source,
        },
        "metaData": {},
    }

    return payload


def submit_document_to_sirius(data, headers):
    SIRIUS_URL = os.environ["SIRIUS_PUBLIC_API_URL"]
    headers = {"Content-Type": "application/json"}

    url = SIRIUS_URL + "documents"

    r = requests.post(url=url, data=data, headers=headers)

    if r.status_code == 201:
        sirius_response = {
            "statusCode": r.status_code,
            "headers": json.dumps(dict(r.headers)),
            "body": r.json,
        }
    elif r.status_code == 400:
        sirius_response = {
            "statusCode": r.status_code,
            "headers": json.dumps(dict(r.headers)),
            "body": "Invalid client id",
        }
    else:
        sirius_response = {
            "statusCode": r.status_code,
            "headers": json.dumps(dict(r.headers)),
            "body": "Error connecting to Sirius Public API",
        }

    return sirius_response
