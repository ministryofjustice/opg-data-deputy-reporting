
import json
import logging
import os

from .helpers import compare_two_dicts
from .sirius_service import build_sirius_url, build_sirius_headers, \
    submit_document_to_sirius

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
    logger.debug(f"Lambda Response: {lambda_response}")

    return lambda_response


def validate_event(event):
    # TODO if there is not a nicer way to do this, there should be
    """
    The request body *should* be validated by API-G before it gets this far,
    but given everything blows up if any of these required fields are missing/wrong
    then it's worth double checking here, and providing integrators with a meaningful
    error message

    Args:
        event: AWS event json

    Returns:
        tuple: valid boolean, error list
    """

    required_body_structure = {
        "supporting_document": {
            "data": {
                "attributes": {"submission_id": 0},
                "file": {"name": "string", "mimetype": "string", "source": "string"},
            }
        }
    }

    errors = compare_two_dicts(
        required_body_structure, json.loads(event["body"]), missing=[]
    )

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
    logger.debug(f"Sirius Payload: {payload}")

    return json.dumps(payload)


# # Helpers
#
#
# def compare_two_dicts(required_structure, test_dict, path="", missing=[]):
#
#     for key in required_structure:
#         if key not in test_dict:
#             missing_item = f"{path}->{key}"
#             if missing_item not in missing:
#                 missing.append(missing_item)
#         else:
#             if type(required_structure[key]) is dict:
#                 if path == "":
#                     path = key
#                 else:
#                     path = path + "->" + key
#                 compare_two_dicts(
#                     required_structure[key], test_dict[key], path, missing
#                 )
#             else:
#                 if isinstance(test_dict[key], type(None)):
#                     missing.append(f"{path}->{key}")
#                 elif type(test_dict[key]) == str and len(test_dict[key]) == 0:
#                     missing_item = f"{path}->{key}"
#
#                     if missing_item not in missing:
#                         missing.append(missing_item)
#
#     return missing
#
#
# # Sirius API Service
#
#
# def build_sirius_url(base_url, api_route, endpoint):
#     """
#     Builds the url for the endpoint from variables (probably saved in env vars)
#
#     Args:
#         base_url: URL of the Sirius server
#         api_route: path to public api
#         endpoint: endpoint
#     Returns:
#         string: url
#     """
#     SIRIUS_URL = urljoin(base_url, api_route)
#     url = urljoin(SIRIUS_URL, endpoint)
#
#     if urlparse(url).scheme not in ["https", "http"]:
#         logger.info("Unable to build Sirius URL")
#         return False
#
#     return url
#
#
# def get_secret(environment):
#     """
#     Gets and decrypts the JWT secret from AWS Secrets Manager for the chosen environment
#     This was c&p directly from AWS Secrets Manager...
#
#     Args:
#         environment: AWS environment name
#     Returns:
#         JWT secret
#     Raises:
#         ClientError
#     """
#     secret_name = f"{environment}/jwt-key"
#     region_name = "eu-west-1"
#
#     session = boto3.session.Session()
#     client = session.client(service_name="secretsmanager", region_name=region_name)
#
#     try:
#         get_secret_value_response = client.get_secret_value(SecretId=secret_name)
#         secret = get_secret_value_response["SecretString"]
#     except ClientError as e:
#         logger.info("Unable to get secret from Secrets Manager")
#         raise e
#
#     return secret
#
#
# def build_sirius_headers(content_type="application/json"):
#     """
#     Builds headers for Sirius request, including JWT auth
#
#     Args:
#         content_type: string, defaults to 'application/json'
#     Returns:
#         Header dictionary with content type and auth token
#     """
#     environment = os.environ["ENVIRONMENT"]
#     encoded_jwt = jwt.encode(
#         {
#             "session-data": "publicapi@opgtest.com",
#             "iat": datetime.datetime.utcnow(),
#             "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
#         },
#         get_secret(environment),
#         algorithm="HS256",
#     )
#
#     return {
#         "Content-Type": content_type,
#         "Authorization": "Bearer " + encoded_jwt.decode("UTF8"),
#     }
#
#
# def submit_document_to_sirius(url, data, headers):
#     """
#     Sends POST to Sirius
#
#     Args:
#         url: POST url
#         data: data payload
#         headers: request headers
#
#     Returns:
#         AWS Lambda style dict
#     """
#     response_messages = {
#         400: "Invalid payload",
#         401: "Unauthorised",
#         403: "Forbidden",
#         404: "Error connecting to Sirius Public API",
#     }
#
#     default_error = "An unknown error occurred connecting to the Sirius Public API"
#
#     try:
#
#         r = requests.post(url=url, data=data, headers=headers)
#
#         status_code = r.status_code
#         logger.debug(f"Sirius reponse code: {status_code}")
#
#         if status_code == 201:
#             sirius_response = {
#                 "isBase64Encoded": False,
#                 "statusCode": status_code,
#                 "headers": dict(r.headers),
#                 "body": r.content.decode("UTF-8"),
#             }
#
#         else:
#             logger.info(
#                 f"Unable to send request to Sirius, response code {status_code}"
#             )
#             sirius_response = {
#                 "isBase64Encoded": False,
#                 "statusCode": status_code,
#                 "headers": {"Content-Type": "application/json"},
#                 "body": response_messages[status_code]
#                 if status_code in response_messages
#                 else default_error,
#             }
#
#     except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
#         logger.info(f"Unable to send request to Sirius, server not available")
#         sirius_response = {
#             "isBase64Encoded": False,
#             "statusCode": 404,
#             "headers": {"Content-Type": "application/json"},
#             "body": f"{default_error} - {e}",
#         }
#
#     return sirius_response
