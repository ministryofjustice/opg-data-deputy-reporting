import requests
import os
import logging

from aws_xray_sdk.core import patch_all

patch_all()


def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(os.environ["LOGGER_LEVEL"])

    api_host = os.environ["BASE_URL"]

    logger.info(f"Starting healthcheck on {api_host}")
    logger.debug(f"Event: {event}")
    logger.debug(f"Context: {context}")

    r = requests.get(api_host + "/api/health-check/service-status", verify=False)
    response = {
        "statusCode": r.status_code,
        "headers": {"myheader": "response"},
        "body": r.text,
    }
    return response
