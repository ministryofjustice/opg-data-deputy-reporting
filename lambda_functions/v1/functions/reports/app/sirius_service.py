import datetime
import logging
import os
from urllib.parse import urljoin, urlparse

import boto3
import jwt
import requests
from botocore.exceptions import ClientError


# Sirius API Service

logger = logging.getLogger()

try:
    logger.setLevel(os.environ["LOGGER_LEVEL"])
except KeyError:
    logger.setLevel("INFO")

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("[%(levelname)s] [in %(funcName)s:%(lineno)d] %(message)s")
)
logger.addHandler(handler)


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

    if urlparse(url).scheme not in ["https", "http"]:
        logger.info("Unable to build Sirius URL")
        return False

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
        logger.info("Unable to get secret from Secrets Manager")
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
        logger.debug(f"Sirius reponse code: {status_code}")

        if status_code == 201:
            sirius_response = {
                "isBase64Encoded": False,
                "statusCode": status_code,
                "headers": dict(r.headers),
                "body": r.content.decode("UTF-8"),
            }

        else:
            logger.info(
                f"Unable to send request to Sirius, response code {status_code}"
            )
            sirius_response = {
                "isBase64Encoded": False,
                "statusCode": status_code,
                "headers": {"Content-Type": "application/json"},
                "body": response_messages[status_code]
                if status_code in response_messages
                else default_error,
            }

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logger.info(f"Unable to send request to Sirius, server not available")
        sirius_response = {
            "isBase64Encoded": False,
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": f"{default_error} - {e}",
        }

    return sirius_response
