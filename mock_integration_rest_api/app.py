#!/usr/bin/env python3
import boto3
import connexion
import os
import json
from flask import Response
from connexion.exceptions import OAuthProblem
from moto import mock_secretsmanager

from lambda_functions.v1.functions.reports.app.reports import (
    lambda_handler as rep_lambda_handler,
)

from lambda_functions.v1.functions.supporting_docs.app.supporting_docs import (
    lambda_handler as sup_lambda_handler,
)

mockingEnvironment = os.environ.get("MOCKING_ENV")
os.environ["BASE_URL"] = "http://localhost:4343"
os.environ["SIRIUS_BASE_URL"] = "http://localhost:5001"
os.environ["SIRIUS_PUBLIC_API_URL"] = "api/public/v1/"
os.environ["LOGGER_LEVEL"] = "DEBUG"
os.environ["JWT_SECRET"] = "THIS_IS_MY_SECRET_KEY"
os.environ["ENVIRONMENT"] = "local"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"


def healthcheck():
    return "healthy"


TOKEN_DB = {"asdf1234567890": {"uid": 100}}


def apikey_auth(token, required_scopes):
    info = TOKEN_DB.get(token, None)

    if not info:
        raise OAuthProblem("Invalid token")

    return info


@mock_secretsmanager
def addReportDocument(caseref, body):
    conn = boto3.client("secretsmanager", region_name="eu-west-1")
    conn.create_secret(Name="local/jwt-key", SecretString="mock_jwt_token")
    event = {
        "headers": "fake headers",
        "pathParameters": {"caseref": caseref},
        "body": json.dumps(body),
    }

    response = rep_lambda_handler(event, "fakecontext")

    print(response)
    print(response["body"])
    formattedresponse = Response(
        response["body"], status=201, mimetype="application/json"
    )

    return formattedresponse


@mock_secretsmanager
def addReportSupportingDocument(caseref, id, body):
    conn = boto3.client("secretsmanager", region_name="eu-west-1")
    conn.create_secret(Name="local/jwt-key", SecretString="mock_jwt_token")
    event = {
        "headers": "fake headers",
        "pathParameters": {"caseref": caseref, "id": id},
        "body": json.dumps(body),
    }

    response = sup_lambda_handler(event, "fakecontext")

    formattedresponse = Response(
        response["body"], status=201, mimetype="application/json"
    )

    return formattedresponse


sirius_server = connexion.App(__name__)
sirius_server.add_api("deputy-reporting-openapi.yml")
sirius_server.run(port=4343)