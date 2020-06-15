import json
import os
import uuid

import boto3
import requests
from requests_aws4auth import AWS4Auth

# Setup Data


aws_dev_config = {
    "AWS_REGION": "eu-west-1",
    "AWS_SERVICE": "execute-api",
    "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
    "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
    "AWS_SESSION_TOKEN": os.environ["AWS_SESSION_TOKEN"],
    "name": "AWS Dev",
    "url": "https://dev.deputy-reporting.api.opg.service.justice.gov.uk/v1",
    "security": "aws_signature",
    "case_ref": "6404835T",
    "report_id": "33ea0382-cfc9-4776-9036-667eeb68fa4b",
    "sup_doc_id": None,
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

configs_to_test = [mock_config, aws_dev_config]


# Data persisted between tests

uploaded_reports = []
uploaded_supporting_docs = []
uploaded_checklists = []


all_records = []


def send_a_request(url, method, payload, test_config):
    headers = {}
    body = json.dumps(payload)

    if test_config["security"] == "token":
        auth = None
        headers = {
            "Authorization": "asdf1234567890",
            "Content-Type": "application/json",
        }
    else:
        if test_config["AWS_ACCESS_KEY_ID"] == "testing":
            print("Your AWS creds are not set properly")

        boto3.setup_default_session(region_name=test_config["AWS_REGION"])

        auth = AWS4Auth(
            test_config["AWS_ACCESS_KEY_ID"],
            test_config["AWS_SECRET_ACCESS_KEY"],
            test_config["AWS_REGION"],
            test_config["AWS_SERVICE"],
            session_token=test_config["AWS_SESSION_TOKEN"],
        )

    print(f"headers: {headers}")
    print(f"auth: {auth}")

    response = requests.request(method, url, auth=auth, data=body, headers=headers)
    return response.status_code, response.text


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def create_record(returned_data):
    pass
    # r = returned_data
    #
    # child_record = True if r["data"]["attributes"]["parent_id"] is not None else False
    #
    # record = {
    #     "document_type": r["data"]["type"],
    #     "document_id": r["data"]["id"],
    #     "submission_id": r["data"]["attributes"]["submission_id"],
    #     "parent_id": r["data"]["attributes"]["parent_id"],
    # }
    #
    # if child_record:
    #     parent_id = r["data"]["attributes"]["parent_id"]
    #     parent_record = [p for p in all_records if p["document_id"] == parent_id][0]
    #     parent_record["children"].append(record)
    #
    #     return print(f'Added child record {r["data"]["id"]} to parent {parent_id}')
    #     return f'Added child record {r["data"]["id"]} to parent {parent_id}'
    # else:
    #     record["children"] = []
    #     record["amendments"] = []
    #     all_records.append(record)
    #
    #     print(f'Added parent record {r["data"]["id"]}')
    #     return f'Added parent record {r["data"]["id"]}'


def update_record(returned_data, original_record_id):
    pass
    # r = returned_data
    #
    # original_record = [
    #     r for r in all_records if r["document_id"] == original_record_id
    # ][0]
    #
    # record = {
    #     "document_type": r["data"]["type"],
    #     "document_id": r["data"]["id"],
    #     "submission_id": r["data"]["attributes"]["submission_id"],
    #     "amendment": len(original_record["amendments"]) + 1,
    # }
    #
    # original_record["amendments"].append(record)
    #
    # print(f"Updated record with document_id: {original_record_id}")
    # return f"Updated record with document_id: {original_record_id}"
