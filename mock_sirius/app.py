#!/usr/bin/env python3
import connexion
import requests
import os
from flask import Response
from connexion.exceptions import OAuthProblem

mockingEnvironment = os.environ.get("MOCKING_ENV")


def healthcheck():
    return "healthy"


TOKEN_DB = {"asdf1234567890": {"uid": 100}}


def apikey_auth(token, required_scopes):
    info = TOKEN_DB.get(token, None)

    if not info:
        raise OAuthProblem("Invalid token")

    return info


def addReportDocument(caseref):
    response = requests.post(
        "http://" + mockingEnvironment + ":5001/clients/" + caseref + "/reports"
    )
    if response.status_code == 200:
        responsegenerated = Response(
            response.text, status=201, mimetype="application/json"
        )
    else:
        responsegenerated = Response(
            response.text, status=response.status_code, mimetype="application/json"
        )

    return responsegenerated


def addReportSupportingDocument(caseref, id):
    response = requests.post(
        "http://"
        + mockingEnvironment
        + ":5001/clients/"
        + caseref
        + "/reports/"
        + id
        + "/supportingdocuments"
    )
    if response.status_code == 200:
        responsegenerated = Response(
            response.text, status=201, mimetype="application/json"
        )
    else:
        responsegenerated = Response(
            response.text, status=response.status_code, mimetype="application/json"
        )
    return responsegenerated


sirius_server = connexion.App(__name__)
sirius_server.add_api("deputy-reporting-openapi.yml", arguments={"mock": "all"})
sirius_server.run(port=4343)
