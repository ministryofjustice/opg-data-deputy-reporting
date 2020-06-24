import os

from lambda_functions.v1.functions.flask_app.app.api import sirius_service
from lambda_functions.v1.functions.flask_app.app.api.helpers import custom_logger

logger = custom_logger("sirius healthcheck")

# def lambda_handler(event, context):
#     logger = logging.getLogger()
#     logger.setLevel(os.environ["LOGGER_LEVEL"])
#
#     api_host = os.environ["SIRIUS_BASE_URL"]
#
#     logger.info(f"Starting healthcheck on {api_host}")
#     logger.debug(f"Event: {event}")
#     logger.debug(f"Context: {context}")
#
#     r = requests.get(api_host + "/api/health-check/service-status", verify=False)
#     response = {
#         "statusCode": r.status_code,
#         "headers": {"myheader": "response"},
#         "body": r.text,
#     }
#     return response
#


def endpoint_handler():

    try:
        SIRIUS_BASE_URL = os.environ["SIRIUS_BASE_URL"]
        API_VERSION = os.environ["API_VERSION"]
    except KeyError as e:
        logger.error(f"{e} not set")
        return "internal server error", 500

    sirius_api_url = sirius_service.build_sirius_url(
        base_url=f"{SIRIUS_BASE_URL}/api/public",
        version=API_VERSION,
        endpoint="health-check/service-status",
    )

    try:
        sirius_response_code, sirius_response = sirius_service.send_get_to_sirius(
            url=sirius_api_url
        )

    except Exception as e:
        logger.error(f"Error sending request to Sirius: {e}")

    return sirius_response, sirius_response_code
