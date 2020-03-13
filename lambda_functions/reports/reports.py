import json
import os
from urllib.parse import urljoin

import requests


def lambda_handler(event, context):
    sirius_payload = transform_event_to_sirius_request(event)

    sirius_response = submit_document_to_sirius(sirius_payload, None)

    return sirius_response


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
    SIRIUS_URL = urljoin(
        os.environ["SIRIUS_BASE_URL"], os.environ["SIRIUS_PUBLIC_API_URL"]
    )

    url = urljoin(SIRIUS_URL, "documents")

    headers = {"Content-Type": "application/json"}

    try:
        r = requests.post(url=url, data=data, headers=headers)

        status_code = r.status_code
        if r.status_code == 201:
            message = r.json

        elif r.status_code == 400:
            message = "Invalid client id"

        else:
            message = "Error connecting to Sirius Public API"

    except requests.exceptions.ConnectionError as e:
        status_code = 404
        message = f"Error connecting to Sirius Public API: {e}"

    sirius_response = {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": headers,
        "body": message,
    }

    return sirius_response
