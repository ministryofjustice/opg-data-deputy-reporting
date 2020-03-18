import base64
import datetime
import json
import logging
import os
from urllib.parse import urljoin

import boto3
import jwt
import requests
from botocore.exceptions import ClientError

# logger = logging.getLogger()
# logger.setLevel(os.environ["LOGGER_LEVEL"])


def lambda_handler(event, context):

    sirius_api_url = build_sirius_url(
        base_url=os.environ["SIRIUS_BASE_URL"],
        api_route=os.environ["SIRIUS_PUBLIC_API_URL"],
        endpoint="documents",
    )
    sirius_payload = transform_event_to_sirius_request(event=event)
    sirius_headers = build_sirius_headers()

    lambda_response = submit_document_to_sirius(
        url=sirius_api_url, data=sirius_payload, headers=sirius_headers
    )

    return lambda_response


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

    return json.dumps(payload)


# Sirius API Service


def build_sirius_url(base_url, api_route, endpoint):
    SIRIUS_URL = urljoin(base_url, api_route)
    url = urljoin(SIRIUS_URL, endpoint)
    return url


def get_secret(environment):
    secret_name = f"{environment}/jwt-key"
    region_name = "eu-west-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    secret = None

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            secret = base64.b64decode(get_secret_value_response["SecretBinary"])

    return secret


def build_sirius_headers(content_type="application/json"):
    encoded_jwt = jwt.encode(
        {
            "session-data": "publicapi@opgtest.com",
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
        },
        get_secret("development"),
        algorithm="HS256",
    )

    return {
        "Content-Type": content_type,
        "Authorization": "Bearer " + encoded_jwt.decode("UTF8"),
    }


def submit_document_to_sirius(url, data, headers):
    response_messages = {
        400: "Invalid Casrec ID",
        401: "Unauthorised",
        403: "Forbidden",
        404: "Error connecting to Sirius Public API",
    }

    default_error = "An unknown error occurred connecting to the Sirius Public API"

    try:
        r = requests.post(url=url, data=data, headers=headers)

        status_code = r.status_code

        if status_code == 201:
            sirius_response = {
                "isBase64Encoded": False,
                "statusCode": status_code,
                "headers": dict(r.headers),
                "body": json.loads(r.content),
            }

        else:
            sirius_response = {
                "isBase64Encoded": False,
                "statusCode": status_code,
                "headers": {"Content-Type": "application/json"},
                "body": response_messages[status_code]
                if status_code in response_messages
                else default_error,
            }

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        sirius_response = {
            "isBase64Encoded": False,
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": default_error,
        }

    return sirius_response
