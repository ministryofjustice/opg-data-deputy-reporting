import datetime
import json
import logging
import os
from urllib.parse import urljoin

import boto3
import jwt
import requests
from botocore.exceptions import ClientError

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
    print(lambda_response)

    return lambda_response


def validate_event(event):
    errors = []
    request_body = json.loads(event["body"])

    try:
        if len(event["pathParameters"]["caseref"]) == 0:
            errors.append("caseRecNumber")
    except (KeyError, TypeError):
        errors.append("caseRecNumber")

    try:
        if len(event["pathParameters"]["id"]) == 0:
            errors.append("caseRecNumber")
    except (KeyError, TypeError):
        errors.append("caseRecNumber")

    try:
        request_body["supporting_document"]["data"]["attributes"]
    except (KeyError, TypeError):
        errors.append("metadata")

    try:
        if 0 == len(
            request_body["supporting_document"]["data"]["attributes"]["report_id"]
        ):
            errors.append("report_id")
    except (KeyError, TypeError):
        errors.append("report_id")

    try:
        if len(request_body["supporting_document"]["data"]["file"]["name"]) == 0:
            errors.append("file_name")
    except (KeyError, TypeError):
        errors.append("file_name")

    try:
        if len(request_body["supporting_document"]["data"]["file"]["mimetype"]) == 0:
            errors.append("file_type")
    except (KeyError, TypeError):
        errors.append("file_type")

    try:
        if len(request_body["supporting_document"]["data"]["file"]["source"]) == 0:
            errors.append("file_source")
    except (KeyError, TypeError):
        errors.append("file_source")

    if len(errors) > 0:
        return False, errors
    else:
        return True, errors


def transform_event_to_sirius_request(event):
    """
    Takes the 'body' from the AWS event and converts it into the right format for the
    Sirius documents endpoint, detailed here:
    tests/test_data/sirius_documents_payload_schema.json

    Args:
        event: json received from API Gateway
    Returns:
        Sirius-style payload, json
    """
    report_id = event["pathParameters"]["id"]
    case_ref = event["pathParameters"]["caseref"]
    request_body = json.loads(event["body"])
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
    print("Payload To Send:")
    print(payload)

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
    environment = os.environ["ENVIRONMENT"]
    encoded_jwt = jwt.encode(
        {
            "session-data": "publicapi@opgtest.com",
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
        },
        get_secret(environment),
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
        print("SIRIUS RETURNS")
        print(status_code)

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
