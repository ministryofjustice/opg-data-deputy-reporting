# Helpers
import logging
import os
import boto3
import base64


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


def compare_two_dicts(required_structure, test_dict, path="", missing=[]):
    for key in required_structure:
        if key not in test_dict:
            missing_item = f"{path}->{key}"
            if missing_item not in missing:
                missing.append(missing_item)
        else:
            if type(required_structure[key]) is dict:
                if path == "":
                    path = key
                else:
                    path = path + "->" + key
                compare_two_dicts(
                    required_structure[key], test_dict[key], path, missing
                )
            else:
                if isinstance(test_dict[key], type(None)):
                    missing.append(f"{path}->{key}")
                elif type(test_dict[key]) == str and len(test_dict[key]) == 0:
                    missing_item = f"{path}->{key}"

                    if missing_item not in missing:
                        missing.append(missing_item)

    return missing


sirius_errors = {
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


def handle_file_source(file):
    if "source" not in file and "s3_reference" in file:
        source = get_encoded_s3_object(
            get_digideps_s3_client(),
            os.environ["DIGIDEPS_S3_BUCKET"],
            file["s3_reference"],
        )
    else:
        source = file["source"]

    return source


def get_digideps_s3_client():
    master_session = boto3.session.Session()
    sts = master_session.client("sts")
    role_arn = os.environ["DIGIDEPS_S3_ROLE_ARN"]
    assume_role_response = sts.assume_role(
        RoleArn=role_arn, RoleSessionName="lambda-in235"
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
    s3_client.download_file(bucket, key, "/tmp/{}".format(key))
    image = open("/tmp/{}".format(key), "rb")
    image_read = image.read()
    image_64_encode = base64.b64encode(image_read).decode("utf-8")

    return image_64_encode
