import os

from . import sirius_service
from .helpers import custom_logger

logger = custom_logger("sirius healthcheck")


def endpoint_handler():

    try:
        SIRIUS_BASE_URL = os.environ["SIRIUS_BASE_URL"]
        SIRIUS_API_VERSION = os.environ["SIRIUS_API_VERSION"]
    except KeyError as e:
        logger.error(f"{e} not set")
        return "internal server error", 500

    sirius_api_url = sirius_service.build_sirius_url(
        base_url=f"{SIRIUS_BASE_URL}/api/public",
        version=SIRIUS_API_VERSION,
        endpoint="health-check/service-status",
    )

    try:
        sirius_response_code, sirius_response = sirius_service.send_get_to_sirius(
            url=sirius_api_url
        )

    except Exception as e:
        logger.error(f"Error sending request to Sirius: {e}")

    return sirius_response, sirius_response_code
