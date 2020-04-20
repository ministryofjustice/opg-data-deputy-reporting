#!/usr/bin/env python3
import json

import connexion
import os
from flask import Response, jsonify, request
import requests


fakedb = {}
mockingEnvironment = os.environ.get("MOCKING_ENV")


def create_document(document):
    # This is only in here because the state setup isn't on the digideps side
    # Normally the provider_states gets called directly via the verification
    requests.post(
        "http://localhost:5001/api/public/v1/pact/provider_states",
        json={"consumer": "OPG Data", "state": "a submitted report"},
    )

    dbresult = fakedb[document["caseRecNumber"]]

    responsegenerated = Response(
        json.dumps(dbresult), status=201, mimetype="application/json"
    )

    return responsegenerated


def provider_states():
    mapping = {
        "a submitted report": setupReport,
        "submitted supporting docs": setupSupportingDocs,
    }
    mapping[request.json["state"]]()
    return jsonify({"result": request.json["state"]})


def setupReport():
    fakedb["1234567T"] = {"uuid": "33ea0382-cfc9-4776-9036-667eeb68fa4b"}
    print(fakedb)


def setupSupportingDocs():
    fakedb["33ea0382-cfc9-4776-9036-667eeb68fa4b"] = {
        "uuid": "33ea0382-cfc9-4776-9036-667eeb68fa4b"
    }


sirius_server = connexion.App(__name__)
sirius_server.add_api("sirius_public_v1.yml")
sirius_server.run(port=5001)
