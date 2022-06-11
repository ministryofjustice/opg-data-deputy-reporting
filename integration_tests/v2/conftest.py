import json
import os
import uuid

import boto3
import requests
import pytest
from faker import Faker
from requests_aws4auth import AWS4Auth

# Setup Data

aws_dev_v2_config = {
    "name": "AWS v2 Dev",
    "url": f"https://{os.getenv('TF_WORKSPACE')}.dev.deputy-reporting.api.opg.service.justice.gov.uk/v2",
    "security": "aws_signature",
    "case_ref": "0319392T",
    "report_id": "16f62da9-db67-46f6-92b0-c212aeb08506",
    "sup_doc_id": "16f62da9-db67-46f6-92b0-c212aeb08506",
    "submission_id": 12345,
    "checklist_id": "123",
    "s3_object_key": "dd_doc_62_15916290546271",
    "s3_test_file": "integration_test_1mb",
    "s3_bucket_name": "pa-uploads-branch-replication",
    "aws_region": "eu-west-1",
    "mock_sirius": True,
}

mock_config = {
    "name": "Local Mock APG Gateway",
    "url": "http://0.0.0.0:4343/v1",
    "security": "token",
    "case_ref": "1234567T",
    "report_id": "33ea0382-cfc9-4776-9036-667eeb68fa4b",
    "submission_id": 12345,
    "checklist_id": "123",
    "s3_object_key": "objectkey",
    "s3_test_file": "integration_test_1mb",
    "s3_bucket_name": "valid-bucket",
    "aws_region": "eu-west-1",
    "mock_sirius": False,
}

configs_to_test = [aws_dev_v2_config]


# Data persisted between tests
all_records = []


@pytest.mark.smoke_test
def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    for test_config in configs_to_test:
        upload_test_doc(test_config=test_config)


@pytest.mark.smoke_test
def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    for test_config in configs_to_test:
        teardown_test_doc(test_config=test_config)


def get_role_name():
    return "integrations-ci" if os.getenv("CI") == "true" else "breakglass"


def filter_none_values(kwargs: dict) -> dict:
    """Returns a new dictionary excluding items where value was None"""
    return {k: v for k, v in kwargs.items() if v is not None}


def assume_session(
    role_session_name: str,
    role_arn: str,
    region_name: str,
    duration_seconds: int = None,
) -> boto3.Session:
    """
    Returns a session with the given name and role.
    If not specified, duration will be set by AWS, probably at 1 hour.
    Region can be overridden by each client or resource spawned from this session.
    """
    assume_role_kwargs = filter_none_values(
        {
            "RoleSessionName": role_session_name,
            "RoleArn": role_arn,
            "DurationSeconds": duration_seconds,
        }
    )
    credentials = boto3.client("sts").assume_role(**assume_role_kwargs)["Credentials"]
    create_session_kwargs = filter_none_values(
        {
            "aws_access_key_id": credentials["AccessKeyId"],
            "aws_secret_access_key": credentials["SecretAccessKey"],
            "aws_session_token": credentials["SessionToken"],
            "region_name": region_name,
        }
    )
    return boto3.Session(**create_session_kwargs)


def upload_test_doc(test_config):
    session = assume_session(
        "assumed_role_session",
        f"arn:aws:iam::248804316466:role/{get_role_name()}",
        region_name=test_config["aws_region"],
    )
    s3_client = session.client(service_name="s3")

    with open(test_config["s3_test_file"], "rb") as f:
        s3_client.put_object(
            Body=f,
            Bucket=test_config["s3_bucket_name"],
            Key=test_config["s3_object_key"],
            ServerSideEncryption="AES256",
        )


def teardown_test_doc(test_config):
    session = assume_session(
        "assumed_role_session",
        f"arn:aws:iam::248804316466:role/{get_role_name()}",
        region_name=test_config["aws_region"],
    )
    s3_resource = session.resource(service_name="s3")
    s3_resource.Object(
        test_config["s3_bucket_name"], test_config["s3_object_key"]
    ).delete()


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

    boto3.setup_default_session(
        region_name=test_config["aws_region"],
    )

    session = assume_session(
        "assumed_role_session",
        f"arn:aws:iam::288342028542:role/{get_role_name()}",
        region_name=test_config["aws_region"],
    )
    credentials = session.get_credentials()

    credentials = credentials.get_frozen_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    token = credentials.token

    auth = AWS4Auth(
        access_key,
        secret_key,
        test_config["aws_region"],
        "execute-api",
        session_token=token,
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
