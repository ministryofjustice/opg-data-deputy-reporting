# Helpers
import logging
import os

from flask import jsonify


def custom_logger(name):
    formatter = logging.Formatter(
        fmt=f"%(asctime)s - %(levelname)s - {name} - in %("
        f"funcName)s:%(lineno)d - %(message)s"
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    try:
        logger.setLevel(os.environ["LOGGER_LEVEL"])
    except KeyError:
        logger.setLevel("INFO")
    logger.addHandler(handler)
    return logger


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


def error_message(code, message):

    return (
        jsonify(
            {
                "isBase64Encoded": False,
                "statusCode": code,
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "error": {
                        "code": custom_api_errors[str(code)]["error_code"],
                        "title": custom_api_errors[str(code)]["error_title"],
                        "message": str(message)
                        if message
                        else custom_api_errors[str(code)]["error_message"],
                    }
                },
            }
        ),
        code,
    )