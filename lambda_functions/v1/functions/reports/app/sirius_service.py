import datetime
import json
import os
from urllib.parse import urljoin, urlparse

import boto3
import jwt
import requests
from botocore.exceptions import ClientError

# Sirius API Service
from .helpers import custom_logger

logger = custom_logger("sirius_service")


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
    r = requests.post(url=url, data=data, headers=headers)

    try:
        if r.status_code == 201:
            response = r.content.decode("UTF-8")
            sirius_response = format_sirius_response(json.loads(response))
        else:
            logger.info(
                f"Unable to send request to Sirius, response code {r.status_code}"
            )
            sirius_response = {
                "data": f"Error sending data to Sirius",
                "sirius_api_status_code": r.status_code,
            }

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logger.info(f"Unable to send request to Sirius, server not available: {e}")
        sirius_response = {
            "data": f"Error sending data to Sirius",
            "sirius_api_status_code": e,
        }

    return sirius_response


def format_sirius_response(sirius_response):
    try:
        return {
            "data": {
                "type": sirius_response["type"],
                "id": sirius_response["uuid"],
                "attributes": {
                    "submission_id": sirius_response["metadata"]["submission_id"]
                },
            }
        }

    except KeyError:
        return {"data": "Error validating Sirius Public API response"}
