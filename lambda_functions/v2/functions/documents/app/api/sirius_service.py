import datetime
import json
import copy
import os
from urllib.parse import urlparse, urlencode

import boto3
import jwt
import requests
from botocore.exceptions import ClientError

from .helpers import custom_logger, get_sirius_base_url

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

    url_parts = [base_url, version, endpoint]

    sirius_url = "/".join([i for i in url_parts if i is not None])

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

    if os.environ["ENVIRONMENT"] == "local":
        client = session.client(
            service_name="secretsmanager",
            region_name=region_name,
            endpoint_url="http://localstack:4566",
            aws_access_key_id="fake",
            aws_secret_access_key="fake",  # pragma: allowlist secret
        )
    else:
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
    secret = get_secret(environment)

    encoded_jwt = jwt.encode(
        {
            "session-data": session_data,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
        },
        secret,
        algorithm="HS256",
    )

    return {
        "Content-Type": content_type,
        "Authorization": "Bearer " + encoded_jwt,
    }


def new_post_to_sirius(url, data, headers, method):
    try:
        if method == "PUT":
            r = requests.put(url=url, data=data, headers=headers)
        else:
            r = requests.post(url=url, data=data, headers=headers)
    except Exception as e:
        return handle_sirius_error(
            error_message="Unable to send document to Sirius",
            error_details=e,
            data=data,
        )

    logger.info(str(r.json()))

    return r.status_code, r.json()


def get_debug_payload(data):
    payload = json.loads(data)
    debug_payload = copy.deepcopy(payload)
    debug_payload["file"]["source"] = "REDACTED"
    return json.dumps(debug_payload)


def new_submit_document_to_sirius(
    data, method="POST", endpoint="documents", url_params=None
):
    debug_payload = get_debug_payload(data)

    try:
        SIRIUS_BASE_URL = os.environ["SIRIUS_BASE_URL"]
        API_VERSION = (
            os.getenv("SIRIUS_API_VERSION")
            if os.environ["USE_MOCK_SIRIUS"] == "0"
            else None
        )
    except KeyError as e:
        return handle_sirius_error(
            error_message="Expected environment variables not set",
            error_details=e,
            data=debug_payload,
        )

    try:
        sirius_api_url = build_sirius_url(
            base_url=get_sirius_base_url(SIRIUS_BASE_URL),
            version=API_VERSION,
            endpoint=endpoint,
            url_params=url_params,
        )
    except Exception as e:
        return handle_sirius_error(
            error_message="Unable to build Siruis URL",
            error_details=e,
            data=debug_payload,
        )

    try:
        headers = build_sirius_headers()
    except Exception as e:
        return handle_sirius_error(
            error_message="Unable to build Sirius headers",
            error_details=e,
            data=debug_payload,
        )

    try:
        sirius_status_code, sirius_response = new_post_to_sirius(
            url=sirius_api_url, data=data, headers=headers, method=method
        )
    except Exception as e:
        return handle_sirius_error(
            error_message="Unable to send " "document to " "Sirius",
            error_details=e,
            data=debug_payload,
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
                data=debug_payload,
            )
        elif sirius_status_code == 400:
            return handle_sirius_error(
                error_code=400,
                error_message="Validation failed in Sirius",
                error_details=sirius_response,
                data=debug_payload,
            )
        else:
            return handle_sirius_error(
                error_code=sirius_status_code,
                error_message=sirius_response,
                data=debug_payload,
            )

    except Exception as e:
        return handle_sirius_error(error_details=e, data=debug_payload)

    return formatted_status_code, formatted_response


def handle_sirius_error(
    error_code=None, error_message=None, error_details=None, data=None
):
    error_code = error_code if error_code else 500
    error_message = (
        error_message if error_message else "Unknown error talking to " "Sirius"
    )

    try:
        sirius_error_details = error_details["detail"]
        error_details = sirius_error_details
    except (KeyError, TypeError):
        error_details = str(error_details) if len(str(error_details)) > 0 else "None"

    message = f"{error_message}, details: {str(error_details)}, payload: {str(data)}"
    return error_code, message


def format_sirius_success(sirius_response_code, sirius_response=None):

    formatted_status_code = sirius_response_code
    formatted_response = {
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

    return formatted_status_code, formatted_response


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

    return r.status_code, sirius_response
