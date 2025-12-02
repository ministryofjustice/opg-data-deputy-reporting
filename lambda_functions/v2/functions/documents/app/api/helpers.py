# Helpers
import base64
import logging
import os
import json

import boto3
from flask import jsonify, abort, request


class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.

    @param dict fmt_dict: Key: logging format attribute pairs. Defaults to {"message": "message"}.
    @param str time_format: time.strftime() format string. Default: "%Y-%m-%dT%H:%M:%S"
    @param str msec_format: Microsecond formatting. Appended at the end. Default: "%s.%03dZ"
    """

    def __init__(
        self,
        fmt_dict: dict = None,
        time_format: str = "%Y-%m-%dT%H:%M:%S",
        msec_format: str = "%s.%03dZ",
    ):
        self.fmt_dict = fmt_dict if fmt_dict is not None else {"message": "message"}
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    def usesTime(self) -> bool:
        """
        Overwritten to look for the attribute in the format dict values instead of the fmt string.
        """
        return "asctime" in self.fmt_dict.values()

    def checkKey(self, record, fmt_val):
        """
        Returns the value if it exists or empty string otherwise to avoid key errors
        """
        return record.__dict__[fmt_val] if fmt_val in record.__dict__ else ""

    def formatMessage(self, record) -> dict:
        """
        Overwritten to return a dictionary of the relevant LogRecord attributes instead of a string.
        We avoid KeyError by returning "" if key doesn't exist.
        """
        return {
            fmt_key: self.checkKey(record, fmt_val)
            for fmt_key, fmt_val in self.fmt_dict.items()
        }

    def format(self, record) -> str:
        """
        Mostly the same as the parent's class method, the difference being that a dict is manipulated and dumped as JSON
        instead of a string.
        """
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)


def custom_logger(name):

    json_formatter = JsonFormatter(
        {
            "level": "levelname",
            "timestamp": "asctime",
            "request_id": "request_id",
            "request_uri": "request_uri",
            "message": "message",
            "status": "status",
            "loggerName": "name",
            "functionName": "funcName",
            "lineNumber": "lineno",
            "source_ip": "source_ip",
            "user_agent": "user_agent",
            "method": "method",
            "protocol": "protocol",
        }
    )

    handler = logging.StreamHandler()
    handler.setFormatter(json_formatter)
    logging.getLogger().handlers.clear()
    logger = logging.getLogger(name)
    try:
        logger.setLevel(os.environ["LOGGER_LEVEL"])
    except KeyError:
        logger.setLevel("INFO")
    logger.addHandler(handler)
    return logger


logger = custom_logger("helpers")


custom_api_errors = {
    "400": {
        "error_code": "OPGDATA-API-INVALIDREQUEST",
        "error_message": "Invalid request, the data is incorrect",
        "error_title": "Invalid Request",
    },
    "401": {
        "error_code": "OPGDATA-API-UNAUTHORISED",
        "error_message": "Unauthorised (no current user and there should be)",
        "error_title": "User is not authorised",
    },
    "403": {
        "error_code": "OPGDATA-API-FORBIDDEN",
        "error_message": "Forbidden - The current user is forbidden from "
        "accessing this data (in this way)",
        "error_title": "Access Denied",
    },
    "404": {
        "error_code": "OPGDATA-API-NOTFOUND",
        "error_message": "That URL is not a valid route, or the item resource "
        "does not exist",
        "error_title": "Page not found",
    },
    "405": {
        "error_code": "OPGDATA-API-NOT-ALLOWED",
        "error_message": "That method is not allowed on this URL",
        "error_title": "Method not allowed",
    },
    "413": {
        "error_code": "OPGDATA-API-FILESIZELIMIT",
        "error_message": "Payload too large, try and upload in smaller chunks",
        "error_title": "Payload too large",
    },
    "415": {
        "error_code": "OPGDATA-API-MEDIA",
        "error_message": "Unsupported media type for this endpoint",
        "error_title": "Unsupported media type",
    },
    "500": {
        "error_code": "OPGDATA-API-SERVERERROR",
        "error_message": "Something unexpected happened internally",
        "error_title": "Internal server error",
    },
    "503": {
        "error_code": "OPGDATA-API-UNAVAILABLE",
        "error_message": "Service is currently unavailable. Please try again " "later",
        "error_title": "Service Unavailable",
    },
}


def get_request_details_for_logs(status=None):
    return {
        "source_ip": request.environ["SOURCE_IP"],
        "user_agent": request.environ["USER_AGENT"],
        "method": request.environ["REQUEST_METHOD"],
        "protocol": request.environ["SERVER_PROTOCOL"],
        "request_uri": request.environ["PATH_INFO"],
        "request_id": request.environ["REQUEST_ID"],
        "status": status,
    }


def validate_request_data(request, request_information, caseref):
    if "application/json" not in request.headers["Content-Type"]:
        request_information["status"] = 415
        logger.error(
            custom_api_errors["415"]["error_message"], extra=request_information
        )
        abort(415)

    try:
        data = request.get_json()
    except Exception as e:
        request_information["status"] = 400
        logger.error(e, extra=request_information)
        abort(400, e)

    if not caseref.isalnum():
        abort(400)

    return data


def error_message(code, message):
    request_id = None
    if "REQUEST_ID" in request.environ:
        request_id = request.environ["REQUEST_ID"]
    return (
        jsonify(
            {
                "isBase64Encoded": False,
                "statusCode": code,
                "headers": {"Content-Type": "application/json"},
                "error": {
                    "id": request_id,
                    "code": custom_api_errors[str(code)]["error_code"],
                    "title": custom_api_errors[str(code)]["error_title"],
                    "detail": (
                        str(message)
                        if message
                        else custom_api_errors[str(code)]["error_message"]
                    ),
                },
            }
        ),
        code,
    )


def get_sirius_base_url(base_url):
    return (
        f"{base_url}"
        if (
            os.environ["ENVIRONMENT"] == "local" or os.environ["USE_MOCK_SIRIUS"] == "1"
        )
        else f"{base_url}/api/public"
    )


def handle_file_source(file):
    if "source" not in file and "s3_reference" in file:

        try:
            bucket = os.environ["DIGIDEPS_S3_BUCKET"]
            if os.environ["ENVIRONMENT"] == "local":
                s3_session = boto3.session.Session()
                s3_client = s3_session.client(
                    "s3",
                    endpoint_url="http://localstack:4566",
                    aws_access_key_id="fake",
                    aws_secret_access_key="fake",  # pragma: allowlist secret
                )
            else:
                s3_client = get_digideps_s3_client()
        except Exception as e:
            logger.error(f"Error handling file: {e}")
            return None

        source = get_encoded_s3_object(
            s3_client=s3_client,
            bucket=bucket,
            key=file["s3_reference"],
        )
    elif "source" in file:
        source = file["source"]
    else:
        source = None
    return source


def get_digideps_s3_client():
    master_session = boto3.session.Session()
    sts = master_session.client("sts")
    role_arn = os.environ["DIGIDEPS_S3_ROLE_ARN"]
    assume_role_response = sts.assume_role(
        RoleArn=role_arn, RoleSessionName="data-deputy-reporting"
    )

    if "Credentials" in assume_role_response:
        assumed_session = boto3.Session(
            aws_access_key_id=assume_role_response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=assume_role_response["Credentials"][
                "SecretAccessKey"
            ],
            aws_session_token=assume_role_response["Credentials"]["SessionToken"],
        )

    return assumed_session.client("s3")


def get_encoded_s3_object(s3_client, bucket, key):
    try:
        # Get the object from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        body = response["Body"]
    except Exception as e:
        logger.error(f"Error fetching object from S3: {e}")
        return None

    try:
        # Read the stream into memory
        image_bytes = body.read()
        image_64_encode = base64.b64encode(image_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"Error encoding object from S3: {e}")
        image_64_encode = None

    return image_64_encode
