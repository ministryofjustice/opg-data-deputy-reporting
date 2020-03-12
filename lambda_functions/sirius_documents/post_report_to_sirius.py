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
        "type": "Report - General",
        "caseRecNumber": case_ref,
        "metadata": {},
        "file": {"name": file_name, "source": source, "type": "application/pdf"},
    }

    return payload


def submit_document_to_sirius(data, headers):
    SIRIUS_URL = os.environ["SIRIUS_PUBLIC_API_URL"]
    headers = {"Content-Type": "application/json"}

    url = SIRIUS_URL + "documents"

    try:
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

    except requests.exceptions.ConnectionError as e:
        sirius_response = {
            "statusCode": 404,
            "headers": headers,
            "body": f"Error connecting to Sirius Public API: {e}",
        }

    return sirius_response
