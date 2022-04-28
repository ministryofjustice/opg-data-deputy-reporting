#!/usr/bin/env python3
import boto3
import connexion
import os
import json
from flask import Response
from connexion.exceptions import OAuthProblem
from moto import mock_secretsmanager, mock_s3, mock_sts

from lambda_functions.v2.functions.documents.app.api import (
    healthcheck,
    reports,
    supporting_docs,
    checklists,
)

# Env variable set here for consistency across CI and local env.
# MOCKING_ENV set externally
mocking_environment = os.environ.get("MOCKING_ENV")
os.environ["BASE_URL"] = "http://localhost:4343"
os.environ["SIRIUS_BASE_URL"] = "http://" + mocking_environment + ":5001"
os.environ["SIRIUS_PUBLIC_API_URL"] = "api/public/v1/"
os.environ["LOGGER_LEVEL"] = "DEBUG"
os.environ["JWT_SECRET"] = "THIS_IS_MY_SECRET_KEY"
os.environ["ENVIRONMENT"] = "local"
os.environ["SESSION_DATA"] = "publicapi@opgtest.com"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["API_VERSION"] = "v2"
os.environ["SIRIUS_API_VERSION"] = "v1"
os.environ["DIGIDEPS_S3_BUCKET"] = "local_bucket"
os.environ["DIGIDEPS_S3_ROLE_ARN"] = "arn:aws:iam::123456789012:role/s3-read-role"

TOKEN_DB = {"asdf1234567890": {"uid": 100}}


def apikey_auth(token, required_scopes):
    info = TOKEN_DB.get(token, None)

    if not info:
        raise OAuthProblem("Invalid token")

    return info


def reporting_healthcheck():
    formatted_response = Response("OK", status=200, mimetype="application/json")
    return formatted_response


@mock_sts
@mock_s3
@mock_secretsmanager
def addReportDocument(caseref, body):
    conn_secrets = boto3.client("secretsmanager", region_name="eu-west-1")
    conn_secrets.create_secret(Name="local/jwt-key", SecretString="mock_jwt_token")

    conn_s3 = boto3.resource("s3")
    conn_s3.create_bucket(Bucket="local_bucket")
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket="local_bucket",
        Key="dd_doc_98765_01234567890123",
        Body="ZmFrZV9jb250ZW50cw==",
    )

    api_response, api_status_code = reports.endpoint_handler(body, caseref)

    formatted_response = Response(
        json.dumps(api_response), status=api_status_code, mimetype="application/json"
    )

    return formatted_response


@mock_sts
@mock_s3
@mock_secretsmanager
def addReportSupportingDocument(caseref, id, body):
    conn = boto3.client("secretsmanager", region_name="eu-west-1")
    conn.create_secret(Name="local/jwt-key", SecretString="mock_jwt_token")

    conn_s3 = boto3.resource("s3")
    conn_s3.create_bucket(Bucket="local_bucket")
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket="local_bucket",
        Key="dd_doc_98765_01234567890123",
        Body="ZmFrZV9jb250ZW50cw==",
    )

    api_response, api_status_code = supporting_docs.endpoint_handler(body, caseref, id)

    formatted_response = Response(
        json.dumps(api_response), status=api_status_code, mimetype="application/json"
    )

    return formatted_response


@mock_secretsmanager
def addReportChecklist(body, caseref, id):
    conn = boto3.client("secretsmanager", region_name="eu-west-1")
    conn.create_secret(Name="local/jwt-key", SecretString="mock_jwt_token")

    api_response, api_status_code = checklists.endpoint_handler(
        body, caseref, id, None, "POST"
    )

    formatted_response = Response(
        json.dumps(api_response), status=api_status_code, mimetype="application/json"
    )

    return formatted_response


def updateReportChecklist():
    return "Not needed for PACT checks currently"


sirius_server = connexion.App(__name__)
sirius_server.add_api("deputy-reporting-openapi.yml")
sirius_server.run(port=4343)
