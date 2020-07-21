import json
import os
import uuid

import boto3
import requests
from boto3.session import Session
from faker import Faker
from requests_aws4auth import AWS4Auth

# Setup Data


aws_dev_config = {
    "name": "AWS Dev",
    "url": "https://in299.dev.deputy-reporting.api.opg.service.justice.gov.uk/v1",
    "security": "aws_signature",
    "case_ref": "42206375",
    "report_id": "123",
    "sup_doc_id": "123",
    "submission_id": 12345,
    "checklist_id": "123",
}

aws_dev_v2_config = {
    "name": "AWS v2 IN-299",
    "url": "https://in298.dev.deputy-reporting.api.opg.service.justice.gov.uk/v2",
    "security": "aws_signature",
    "case_ref": "42206375",
    "report_id": "123",
    "sup_doc_id": "123",
    "submission_id": 12345,
    "checklist_id": "123",
}

mock_config = {
    "name": "Local Mock APG Gateway",
    "url": "http://0.0.0.0:4343/v1",
    "security": "token",
    "case_ref": "1234567T",
    "report_id": "33ea0382-cfc9-4776-9036-667eeb68fa4b",
    "submission_id": 12345,
    "checklist_id": "123",
}

configs_to_test = [aws_dev_v2_config]


# Data persisted between tests
all_records = []


def send_a_request(
    url, method, payload, test_config, extra_headers=None, content_type=None
):
    print(f"Using test_config: {test_config['name']}")
    print(f"url: {url}")
    print(f"method: {method}")
    print(f"payload: {json.dumps(payload, indent=4)}")

    headers = {
        "Content-Type": content_type if content_type else "application/json",
    }

    if extra_headers:
        for h in extra_headers:
            headers[h["header_name"]] = h["header_value"]

    body = json.dumps(payload)

    if test_config["security"] == "token":
        auth = None
        headers["Authorization"] = "asdf1234567890"
    else:
        if os.getenv("AWS_ACCESS_KEY_ID") == "testing":
            print("Your AWS creds are not set properly")

    if "CI" in os.environ:
        role_name = "sirius-ci"
    else:
        role_name = "operator"

    boto3.setup_default_session(region_name="eu-west-1",)

    client = boto3.client("sts")
    client.get_caller_identity()["Account"]

    role_to_assume = f"arn:aws:iam::288342028542:role/{role_name}"

    response = client.assume_role(
        RoleArn=role_to_assume, RoleSessionName="assumed_role"
    )

    session = Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
    )

    client = session.client("sts")
    client.get_caller_identity()["Account"]

    credentials = session.get_credentials()

    credentials = credentials.get_frozen_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    token = credentials.token

    auth = AWS4Auth(
        access_key, secret_key, "eu-west-1", "execute-api", session_token=token,
    )

    response = requests.request(method, url, auth=auth, data=body, headers=headers)

    print(f"response.status_code: {response.status_code}")
    print(f"response: {json.dumps(response.json(), indent=4)}")

    return response.status_code, response.text


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def generate_file_name():
    fake = Faker()
    words = fake.words()

    return "_".join(words)
