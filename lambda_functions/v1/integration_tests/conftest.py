import json
import uuid

import boto3
import requests
from requests_aws4auth import AWS4Auth

# Setup Data

config = {
    "AWS_REGION": "eu-west-1",
    "AWS_SERVICE": "execute-api",
    "AWS_ACCESS_KEY_ID": "ASIAUGIUGGD7L4TXKQAX",
    "AWS_SECRET_ACCESS_KEY": "Z18uw+Y9Zx338xkU5GveDhwrHyip13QitxSM638S",
    "AWS_SESSION_TOKEN": "FwoGZXIvYXdzEMb//////////wEaDNUpX1rW+XIY09hfESK7AUMxBSZAnFfSE"
    "JPDi/ysKi0SILdAsu3UNd+KYojrRpXXdq8ZZK2aHFeGJO0QWauqRBBnOjX5y/"
    "rVnzaGSCoShQL3N1mRJ4Dj5//wA78zrVr6kP4zFNUZsKts+7yXff5tI7Rk4SN"
    "iXhCJkblAjZFkskDJrIpyamIU0emYW5pXEYMox63IuAnyPXGTeKtUaF5YWvg8"
    "YyR9wAf2ryoMZEvHnmdLqWwce/vg7j3FynKZN4tB7PH5Nw61TvBdiIko3ayD9"
    "wUyLTFQ1XBZr6LQg4U10zf+nyPeVGxOtjrhjWxEwB0l2OH8QdWf3HkA5dF229"
    "/acQ==",
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


def send_a_request(url, method, payload):

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
