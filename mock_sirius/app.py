#!/usr/bin/env python3
import connexion
import requests
import os
from flask import Response

mockingEnvironment = os.environ.get("MockingEnvironment")


def healthcheck():
    return "healthy"


def showReportDocument():
    return "show a doc"


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


def addReportSupportingDocument():
    return "supporting doc posted"


sirius_server = connexion.App(__name__)
sirius_server.add_api("deputy-reporting-openapi.yml")
sirius_server.run(port=4343)
