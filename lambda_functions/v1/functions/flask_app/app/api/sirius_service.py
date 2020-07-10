import datetime
import json
import os
from urllib.parse import urlparse, urlencode

import boto3
import jwt
import requests
from botocore.exceptions import ClientError

from .helpers import custom_logger, custom_api_errors

# Sirius API Service

logger = custom_logger("sirius_service")


def build_sirius_url(base_url, version, endpoint, url_params=None):
    """
    Builds the url for the endpoint from variables (probably saved in env vars)

    Args:
        base_url: URL of the Sirius server
        api_route: path to public api
        endpoint: endpoint
    Returns:
        string: url
    """

    sirius_url = f"{base_url}/{version}/{endpoint}"

    if url_params:
        encoded_params = urlencode(url_params)
        url = f"{sirius_url}?{encoded_params}"
    else:
        url = sirius_url

    if urlparse(url).scheme not in ["https", "http"]:
        logger.info("Unable to build Sirius URL")
        raise Exception

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
    session_data = os.environ["SESSION_DATA"]

    encoded_jwt = jwt.encode(
        {
            "session-data": session_data,
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


def new_post_to_sirius(url, data, headers, method):
    try:
        if method == "PUT":
            r = requests.put(url=url, data=data, headers=headers)
        else:
            r = requests.post(url=url, data=data, headers=headers)
    except Exception as e:
        return handle_sirius_error(
            error_message="Unable to send document to Sirius", error_details=e
        )

    return r.status_code, r.json()


def new_submit_document_to_sirius(
    data, method="POST", endpoint="documents", url_params=None
):

    try:
        SIRIUS_BASE_URL = os.environ["SIRIUS_BASE_URL"]
        API_VERSION = os.environ["API_VERSION"]
    except KeyError as e:
        return handle_sirius_error(
            error_message="Expected environment variables not set", error_details=e
        )

    try:
        sirius_api_url = build_sirius_url(
            base_url=f"{SIRIUS_BASE_URL}/api/public",
            version=API_VERSION,
            endpoint=endpoint,
            url_params=url_params,
        )
    except Exception as e:
        return handle_sirius_error(
            error_message="Unable to build Siruis URL", error_details=e
        )

    try:
        headers = build_sirius_headers()
    except Exception as e:
        return handle_sirius_error(
            error_message="Unable to build Sirius headers", error_details=e
        )

    try:
        sirius_status_code, sirius_response = new_post_to_sirius(
            url=sirius_api_url, data=data, headers=headers, method=method
        )

    except Exception as e:
        return handle_sirius_error(
            error_message="Unable to send " "document to " "Sirius", error_details=e,
        )

    try:
        if sirius_status_code in [200, 201]:
            formatted_status_code, formatted_response = format_sirius_success(
                sirius_response_code=sirius_status_code, sirius_response=sirius_response
            )
        elif sirius_status_code == 404:
            return handle_sirius_error(
                error_code=400,
                error_message="Could not verify URL params in " "Sirius",
                error_details=sirius_response,
            )
        elif sirius_status_code == 400:
            return handle_sirius_error(
                error_code=400,
                error_message="Validation failed in Sirius",
                error_details=sirius_response,
            )
        else:
            return handle_sirius_error(
                error_code=sirius_status_code, error_message=sirius_response
            )

    except Exception as e:
        return handle_sirius_error(error_details=e)

    return formatted_status_code, formatted_response


def handle_sirius_error(error_code=None, error_message=None, error_details=None):
    error_code = error_code if error_code else 500
    error_message = (
        error_message if error_message else "Unknown error talking to " "Sirius"
    )

    try:
        sirius_error_details = error_details["detail"]
        error_details = sirius_error_details
    except (KeyError, TypeError):
        error_details = str(error_details) if len(str(error_details)) > 0 else "None"

    message = f"{error_message}, details: {str(error_details)}"
    logger.error(message)
    return error_code, message


def format_sirius_success(sirius_response_code, sirius_response=None):

    formatted_status_code = sirius_response_code
    formatted_response = {
        "data": {
            "type": sirius_response["type"],
            "id": sirius_response["uuid"],
            "attributes": {
                "submission_id": sirius_response["metadata"]["submission_id"],
                "parent_id": sirius_response["parentUuid"]
                if "parentUuid" in sirius_response
                else None,
            },
        }
    }

    return formatted_status_code, formatted_response


# DEPRECATED - use new_submit_document_to_sirius instead
def submit_document_to_sirius(url, data, headers=None, method="POST"):
    logger.info("SENDING DOC TO SIRIUS")
    if not headers:
        headers = build_sirius_headers()

    try:
        if method == "PUT":
            r = requests.put(url=url, data=data, headers=headers)
        else:
            r = requests.post(url=url, data=data, headers=headers)
    except Exception as e:
        print(f"e: {e}")

    try:
        sirius_response_code = r.status_code
        if r.status_code in [200, 201]:
            response = r.content.decode("UTF-8")
            sirius_response = format_sirius_response(
                json.loads(response), sirius_response_code
            )
        else:
            logger.info(
                f"Unable to send request to Sirius, response code {r.status_code}"
            )
            sirius_response = format_sirius_response(
                sirius_response_code=sirius_response_code
            )

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logger.info(f"Unable to send request to Sirius, server not available: {e}")
        sirius_response_code = 500
        sirius_response = format_sirius_response()

    logger.info(f"sirius_response: {sirius_response}")

    return (sirius_response_code, sirius_response)


# DEPRECATED - use format_sirius_success and handle_sirius_error instead
def format_sirius_response(sirius_response=None, sirius_response_code=500):
    if sirius_response is None:
        sirius_response = {}

    try:
        if sirius_response_code in [200, 201]:
            response = {
                "data": {
                    "type": sirius_response["type"],
                    "id": sirius_response["uuid"],
                    "attributes": {
                        "submission_id": sirius_response["metadata"]["submission_id"]
                        if "submission_id" in sirius_response["metadata"]
                        else None,
                        "parent_id": sirius_response["parentUuid"]
                        if "parentUuid" in sirius_response
                        else None,
                    },
                }
            }
        else:
            response = {
                "errors": {
                    "id": "",
                    "code": custom_api_errors[str(sirius_response_code)]["error_code"],
                    "title": custom_api_errors[str(sirius_response_code)][
                        "error_title"
                    ],
                    "detail": custom_api_errors[str(sirius_response_code)][
                        "error_message"
                    ],
                    "meta": {},
                }
            }

    except KeyError:
        response = {
            "errors": {
                "id": "",
                "code": custom_api_errors[str(sirius_response_code)]["error_code"],
                "title": custom_api_errors[str(sirius_response_code)]["error_title"],
                "detail": custom_api_errors[str(sirius_response_code)]["error_message"],
                "meta": {"sirius_error": "Error validating Sirius Public API response"},
            }
        }

    return response


def send_get_to_sirius(url, headers=None):
    if not headers:
        headers = build_sirius_headers()
    r = requests.get(url=url, headers=headers)

    try:
        if r.status_code == 200:
            response = r.content.decode("UTF-8")
            sirius_response = json.loads(response)
        else:
            logger.info(
                f"Unable to send request to Sirius, response code {r.status_code}"
            )
            sirius_response = None

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logger.info(f"Unable to send request to Sirius, server not available: {e}")
        sirius_response = None

    return sirius_response
