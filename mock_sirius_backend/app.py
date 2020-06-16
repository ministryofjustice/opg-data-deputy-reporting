#!/usr/bin/env python3
import json
import connexion
from flask import Response, jsonify, request
import requests


fake_db = {}


def createDeputyDocument(document):
    # This is only in here because the state setup isn't on the digideps side
    # Normally the provider_states gets called directly via the verification
    requests.post(
        "http://localhost:5001/api/public/v1/pact/provider_states",
        json={"consumer": "OPG Data", "state": "a submitted report"},
    )

    db_result = fake_db[document["caseRecNumber"]]

    response_generated = Response(
        json.dumps(db_result), status=201, mimetype="application/json"
    )

    return response_generated


def provider_states():
    mapping = {
        "a submitted report": setup_report,
        "submitted supporting docs": setup_supporting_docs,
    }
    mapping[request.json["state"]]()
    return jsonify({"result": request.json["state"]})


def setup_report():
    fake_db["1234567T"] = {
        "type": "Report",
        "filename": "a9b4fc3616e62_Report_25558511_2018_2019_12345.pdf",
        "mimeType": "application/pdf",
        "metadata": {
            "reporting_period_from": "2019-01-01",
            "reporting_period_to": "2019-12-31",
            "year": 2019,
            "date_submitted": "2020-01-03T09:30:00.001Z",
            "type": "HW",
            "submission_id": 12345,
        },
        "uuid": "33ea0382-cfc9-4776-9036-667eeb68fa4b",
    }
    print(fake_db)


def setup_supporting_docs():
    fake_db["33ea0382-cfc9-4776-9036-667eeb68fa4b"] = {
        "type": "Report - General",
        "filename": "101856f51959a_supportingDoc.pdf",
        "mimeType": "application/pdf",
        "metadata": {
            "submission_id": 12345,
            "report_id": "887deae4-ed28-4c4e-8986-f7616e1b7d36",
        },
        "parentUuid": "887deae4-ed28-4c4e-8986-f7616e1b7d36",
        "uuid": "33ea0382-cfc9-4776-9036-667eeb68fa4b",
    }


sirius_server = connexion.App(__name__)
sirius_server.add_api("sirius_public_v1.yml")
sirius_server.run(port=5001)
