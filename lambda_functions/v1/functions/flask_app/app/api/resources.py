# import os

from flask import Blueprint
from flask import request, jsonify

from lambda_functions.v1.functions.flask_app.app.api import reports, supporting_docs

# version = os.getenv("API_VERSION")

# api = Blueprint("api", __name__, url_prefix=f"/{version}")

version = "flask"
# api = Blueprint("api", __name__, url_prefix=f"/{version}")
api = Blueprint("api", __name__)


@api.route("/healthcheck", methods=["HEAD", "GET"])
def handle_healthcheck():
    response_message = "OK"

    return jsonify(response_message), 200


@api.route("/clients/<caseref>/reports", methods=["POST"])
def handle_reports(caseref):
    print(f"caseref: {caseref}")
    response_data, response_status = reports.endpoint_handler(
        data=request.get_json(), caseref=caseref
    )

    return jsonify(response_data), response_status


@api.route("/clients/<caseref>/reports/<id>/supportingdocuments", methods=["POST"])
def handle_supporting_docs(caseref, id):
    response_data, response_status = supporting_docs.endpoint_handler(
        data=request.get_json(), caseref=caseref, id=id
    )

    return jsonify(response_data), response_status
