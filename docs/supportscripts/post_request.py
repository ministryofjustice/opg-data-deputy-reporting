import boto3
import requests
from requests_aws4auth import AWS4Auth
import json
from boto3.session import Session


def try_request():
    headers = {
        "Content-Type": "application/pdf",
    }

    client = boto3.client("sts")
    account_id = client.get_caller_identity()["Account"]
    print(account_id)

    role_to_assume = "arn:aws:iam::248804316466:role/operator"
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

    method = "POST"
    payload = {
        "report": {
            "data": {
                "type": "reports",
                "attributes": {
                    "submission_id": 12345,
                    "reporting_period_from": "2019-01-01",
                    "reporting_period_to": "2019-12-31",
                    "year": 2019,
                    "date_submitted": "2020-01-03T09:30:00.001Z",
                    "type": "PF",
                },
                "file": {
                    "name": "blah.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }

    url = "https://sq25usy81d.execute-api.eu-west-1.amazonaws.com/v1/flask/clients/33205624/reports"
    # url = "https://sq25usy81d.execute-api.eu-west-1.amazonaws.com/v1/flask/clients/33205624/reports"

    body = json.dumps(payload)

    response = requests.request(
        method=method, url=url, auth=auth, data=body, headers=headers
    )

    print(response.text)
    print(response.status_code)


try_request()
