import json
import uuid

import boto3
import requests
from requests_aws4auth import AWS4Auth
import os

# Setup Data


config = {
    "AWS_REGION": "eu-west-1",
    "AWS_SERVICE": "execute-api",
    "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
    "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
    "AWS_SESSION_TOKEN": os.environ["AWS_SESSION_TOKEN"],
    "BASE_URL": "https://dev.deputy-reporting.api.opg.service.justice.gov.uk",
    "VERSION": "v1",
    "FLASK_BASE_URL": "https://dev.deputy-reporting.api.opg.service.justice.gov.uk",
    "FLASK_VERSION": "flask",
    "GOOD_CASEREF": "6404835T",
    "BAD_CASEREF": "this_is_not_a_case",
}


urls_to_test = [
    f"{config['BASE_URL']}/{config['VERSION']}",
    # f"{config['FLASK_BASE_URL']}/{config['FLASK_VERSION']}"
]

# Data persisted between tests

uploaded_reports = []
uploaded_supporting_docs = []
uploaded_checklists = []


all_records = []


def send_a_request(url, method, payload):

    print(f"config['AWS_ACCESS_KEY_ID']: {config['AWS_ACCESS_KEY_ID']}")
    if config["AWS_ACCESS_KEY_ID"] == "testing":
        print("Your AWS creds are not set properly")

    boto3.setup_default_session(region_name=config["AWS_REGION"])

    headers = {}
    body = json.dumps(payload)

    auth = AWS4Auth(
        config["AWS_ACCESS_KEY_ID"],
        config["AWS_SECRET_ACCESS_KEY"],
        config["AWS_REGION"],
        config["AWS_SERVICE"],
        session_token=config["AWS_SESSION_TOKEN"],
    )
    response = requests.request(method, url, auth=auth, data=body, headers=headers)
    return response.status_code, response.text


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def create_record(returned_data):

    r = returned_data

    child_record = True if r["data"]["attributes"]["parent_id"] is not None else False

    record = {
        "document_type": r["data"]["type"],
        "document_id": r["data"]["id"],
        "submission_id": r["data"]["attributes"]["submission_id"],
        "parent_id": r["data"]["attributes"]["parent_id"],
    }

    if child_record:
        parent_id = r["data"]["attributes"]["parent_id"]
        parent_record = [p for p in all_records if p["document_id"] == parent_id][0]
        parent_record["children"].append(record)

        return print(f'Added child record {r["data"]["id"]} to parent {parent_id}')
        return f'Added child record {r["data"]["id"]} to parent {parent_id}'
    else:
        record["children"] = []
        record["amendments"] = []
        all_records.append(record)

        print(f'Added parent record {r["data"]["id"]}')
        return f'Added parent record {r["data"]["id"]}'


def update_record(returned_data, original_record_id):
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
    return f"Updated record with document_id: {original_record_id}"
