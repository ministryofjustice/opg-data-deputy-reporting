import json
import logging
import os

import requests


def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(os.environ["LOGGER_LEVEL"])

    sirius_payload = get_data_from_event(event)

    try:
        sirius_response = submit_document_to_sirius(sirius_payload, None)
        response = {
            "statusCode": sirius_response.status_code,
            "headers": json.dumps(dict(sirius_response.headers)),
            # TODO this is a hack because I cba to rebuild the mock sirius container
            #  right now - we shouldn't have to map like this
            "body": {"uuid": json.loads(sirius_response.content)},
        }
    except ConnectionError:
        response = {
            "statusCode": 404,
            "headers": {},
            "body": "Error connecting to Sirius",
        }
    return json.dumps(response)


# Sirius API Service


def get_data_from_event(event):
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

    return json.dumps(payload)


def submit_document_to_sirius(data, headers):
    SIRIUS_URL = "http://0.0.0.0:5555/api/public/v1/"
    headers = {"Content-Type": "application/json"}

    url = SIRIUS_URL + "documents"
    r = requests.post(url=url, data=data, headers=headers)

    return r
