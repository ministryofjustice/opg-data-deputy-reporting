# import os

from flask import Blueprint, abort, request, jsonify

from . import reports, supporting_docs, checklists, healthcheck
from .helpers import error_message

# api = Blueprint("api", __name__, url_prefix=f"/{version}")


# version = os.getenv("API_VERSION")
version = "flask"
api = Blueprint("api", __name__, url_prefix=f"/{version}")
# api = Blueprint("api", __name__)


@api.route("/reporting_healthcheck", methods=["HEAD", "GET"])
def handle_reporting_healthcheck():
    response_message = "OK"

    return jsonify(response_message), 200


@api.route("/healthcheck", methods=["HEAD", "GET"])
def handle_healthcheck():
    response_data, response_status = healthcheck.endpoint_handler()

    return jsonify(response_data), response_status


@api.route("/clients/<caseref>/reports", methods=["POST"])
def handle_reports(caseref):
    print(f"caseref: {caseref}")

    try:
        data = request.get_json()
        print(f"data: {data}")
    except Exception as e:
        abort(400, e)

    if request.headers["Content-Type"] != "application/json":
        abort(415)

    response_data, response_status = reports.endpoint_handler(
        data=data, caseref=caseref
    )

    return jsonify(response_data), response_status


@api.route("/clients/<caseref>/reports/<id>/supportingdocuments", methods=["POST"])
def handle_supporting_docs(caseref, id):

    print(f"request.method: {request.method}")

    try:
        data = request.get_json()
        print(f"data: {data}")
    except Exception as e:
        abort(400, e)

    if request.headers["Content-Type"] != "application/json":
        abort(415)

    response_data, response_status = supporting_docs.endpoint_handler(
        data=data, caseref=caseref, id=id
    )

    return jsonify(response_data), response_status


@api.route("/clients/<caseref>/reports/<id>/checklists/<checklistId>", methods=["PUT"])
def handle_checklists_update(caseref, id, checklistId):
    try:
        data = request.get_json()
        print(f"data: {data}")
    except Exception as e:
        abort(400, e)
    if request.headers["Content-Type"] != "application/json":
        abort(415)

    response_data, response_status = checklists.endpoint_handler(
        data=data, caseref=caseref, id=id, checklist_id=checklistId
    )

    return jsonify(response_data), response_status


@api.route("/clients/<caseref>/reports/<id>/checklists", methods=["POST"])
def handle_checklists(caseref, id):
    try:
        data = request.get_json()
        print(f"data: {data}")
    except Exception as e:
        abort(400, e)

    if request.headers["Content-Type"] != "application/json":
        abort(415)

    response_data, response_status = checklists.endpoint_handler(
        data=data, caseref=caseref, id=id, checklist_id=None
    )

    return jsonify(response_data), response_status


@api.app_errorhandler(400)
def handle400(error=None):
    return error_message(400, error)


@api.app_errorhandler(405)
def handle405(error=None):
    return error_message(405, error)


@api.app_errorhandler(404)
def handle404(error=None):
    return error_message(404, error)


@api.app_errorhandler(415)
def handle415(error=None):
    return error_message(415, error)
