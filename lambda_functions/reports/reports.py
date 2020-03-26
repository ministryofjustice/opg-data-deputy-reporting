import datetime
import json
import logging
import os
from urllib.parse import urljoin

import boto3
import jwt
import requests
from botocore.exceptions import ClientError
from requests_toolbelt.multipart import decoder

logger = logging.getLogger()
if __name__ == "__main__":
    logger.setLevel(os.environ["LOGGER_LEVEL"])


def lambda_handler(event, context):
    """

    Args:
        event: json received from API Gateway
        context:
    Returns:
        Response from Sirius in AWS Lambda format, json
    """

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
    """
    Takes the 'body' from the AWS event and converts it into the right format for the
    Sirius documents endpoint, detailed here:
    tests/test_data/sirius_documents_payload.json

    Args:
        event: json received from API Gateway
    Returns:
        Sirius-style payload, json
    """
    content_type_header = event["headers"]["Content-Type"]

    case_ref = event["pathParameters"]["caseref"]

    request_body = json.loads(event["body"])["body"].encode()

    # request_data = json.loads(
    #     decoder.MultipartDecoder(request_body, content_type_header).parts[0].text
    # )

    file_data = (
        decoder.MultipartDecoder(request_body, content_type_header).parts[1].text
    )

    payload = {
        "type": "Report - General",
        "caseRecNumber": case_ref,
        "metadata": {},
        "file": {"name": "file_name", "source": file_data, "type": "application/pdf"},
    }

    return json.dumps(payload)


# Sirius API Service


def build_sirius_url(base_url, api_route, endpoint):
    """
    Builds the url for the endpoint from variables (probably saved in env vars)

    Args:
        base_url: URL of the Sirius server
        api_route: path to public api
        endpoint: endpoint
    Returns:
        string: url
    """
    SIRIUS_URL = urljoin(base_url, api_route)
    url = urljoin(SIRIUS_URL, endpoint)
    return url


def get_secret(environment):
    """
    Gets and decrypts the JWT secret from AWS Secrets Manager for the chosen environment
    This was c&p directly from AWS Secrets Manager...

    Args:
        environment: AWS environment name
    Returns:
        JWT secret
    Raises:
        ClientError
    """
    secret_name = f"{environment}/jwt-key"
    region_name = "eu-west-1"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response["SecretString"]
    except ClientError as e:
        raise e

    return secret


def build_sirius_headers(content_type="application/json"):
    """
    Builds headers for Sirius request, including JWT auth

    Args:
        content_type: string, defaults to 'application/json'
    Returns:
        Header dictionary with content type and auth token
    """

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
    """
    Sends POST to Sirius

    Args:
        url: POST url
        data: data payload
        headers: request headers

    Returns:
        AWS Lambda style dict
    """
    response_messages = {
        400: "Invalid payload",
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
                "body": r.content.decode("UTF-8"),
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
            "body": f"{default_error} - {e}",
        }

    return sirius_response
