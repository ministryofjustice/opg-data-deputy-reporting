#!/usr/env/bin python3
from flask import Flask, jsonify, request
import requests

fakedb = {}

app = Flask(__name__)


@app.route("/clients/<caseref>/reports", methods=["POST"])
def post_report(caseref):
    # This is just to show how we can mock endpoint.
    # This would be called by the real state setup.
    requests.post(
        "http://localhost:5001/pact/provider_states",
        json={"consumer": "OPG Data", "state": "a submitted report"},
    )
    casejson = fakedb[caseref]
    response = jsonify(**casejson)
    return response


@app.route("/pact/provider_states", methods=["POST"])
def provider_states():
    mapping = {"a submitted report": setupReport}
    mapping[request.json["state"]]()
    return jsonify({"result": request.json["state"]})


def setupReport():
    fakedb["27493727"] = {
        "data": {
            "type": "reports",
            "id": "33ea0382-cfc9-4776-9036-667eeb68fa4b",
            "attributes": {
                "reporting_period_from": "2013-02-01",
                "reporting_period_to": "2013-02-01",
                "year": "2019",
                "date_submitted": "2015-08-06T16:53:10.123+01:00",
                "type": "PF",
            },
        }
    }


if __name__ == "__main__":
    app.run(debug=True, port=5001)
