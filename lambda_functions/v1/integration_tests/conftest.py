import datetime
import json
import os
import uuid

import boto3
from boto3.session import Session

import requests
from requests_aws4auth import AWS4Auth
from faker import Faker

# Setup Data


aws_dev_config = {
    "name": "AWS Dev",
    "url": "https://sq25usy81d.execute-api.eu-west-1.amazonaws.com/v1",
    "security": "aws_signature",
    "case_ref": "33205624",
    "report_id": "123",
    "sup_doc_id": "123",
    "submission_id": 12345,
    "checklist_id": "123",
}

aws_flask_config = {
    "name": "AWS Flask",
    "url": "https://sq25usy81d.execute-api.eu-west-1.amazonaws.com/v1",
    "security": "aws_signature",
    "case_ref": "33205624",
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

configs_to_test = [aws_dev_config]


# Data persisted between tests
all_records = []


def send_a_request(
    url, method, payload, test_config, extra_headers=None, content_type=None
):
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
    account_id = client.get_caller_identity()["Account"]
    print(account_id)

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
    account_id = client.get_caller_identity()["Account"]
    print(account_id)

    credentials = session.get_credentials()

    credentials = credentials.get_frozen_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    token = credentials.token

    auth = AWS4Auth(
        access_key, secret_key, "eu-west-1", "execute-api", session_token=token,
    )

    response = requests.request(method, url, auth=auth, data=body, headers=headers)
    print(str(response.text))
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


def create_record(returned_data=None, file_name=None, config_name=None):
    # pass
    try:
        r = returned_data
    except Exception:
        return "failed to create record"

    child_record = True if r["data"]["attributes"]["parent_id"] is not None else False

    record = {
        "document_type": r["data"]["type"],
        "document_id": r["data"]["id"],
        "submission_id": r["data"]["attributes"]["submission_id"],
        "parent_id": r["data"]["attributes"]["parent_id"],
        "file_name": file_name,
    }

    if child_record:
        parent_id = r["data"]["attributes"]["parent_id"]
        parent_record = [p for p in all_records if p["document_id"] == parent_id][0]
        parent_record["children"].append(record)

        print(f'Added child record {r["data"]["id"]} to parent {parent_id}')

    else:
        record["children"] = []
        record["amendments"] = []
        all_records.append(record)

        print(f'Added parent record {r["data"]["id"]}')

    write_record(config_name=config_name)


def update_record(returned_data, original_record_id, config_name=None):
    # pass
    r = returned_data

    original_record = [
        r for r in all_records if r["document_id"] == original_record_id
    ][0]

    record = {
        "document_type": r["data"]["type"],
        "document_id": r["data"]["id"],
        "submission_id": r["data"]["attributes"]["submission_id"],
        "amendment": len(original_record["amendments"]) + 1,
    }

    original_record["amendments"].append(record)

    print(f"Updated record with document_id: {original_record_id}")
    write_record(config_name=config_name)


def write_record(config_name):

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    json_records = json.dumps(all_records, indent=4)

    with open(f"{config_name}_{date}_updates.json", "w") as outfile:
        outfile.write(json_records)
