import os

from flask import Blueprint, abort, request, jsonify

from . import reports, supporting_docs, checklists, healthcheck
from .helpers import (
    custom_logger,
    error_message,
    get_request_details_for_logs,
    validate_request_data,
)

logger = custom_logger("resources")

version = os.getenv("API_VERSION")
api = Blueprint("api", __name__, url_prefix=f"/{version}")


@api.route("/reporting_healthcheck", methods=["HEAD", "GET"])
def handle_reporting_healthcheck():
    response_message = "OK"

    return jsonify(response_message), 200


@api.route("/healthcheck", methods=["HEAD", "GET"])
def handle_healthcheck():
    response_data, response_status = healthcheck.endpoint_handler()
    logger.info(
        response_data, extra=get_request_details_for_logs(status=response_status)
    )
    return jsonify(response_data), response_status


@api.route("/clients/<caseref>/reports", methods=["POST"])
def handle_reports(caseref):
    data = validate_request_data(request, get_request_details_for_logs(), caseref)

    response_data, response_status = reports.endpoint_handler(
        data=data, caseref=caseref
    )

    if response_status in [201, 200]:
        logger.info(
            response_data, extra=get_request_details_for_logs(status=response_status)
        )
        return jsonify(response_data), response_status
    else:
        logger.error(
            response_data, extra=get_request_details_for_logs(status=response_status)
        )
        abort(response_status, description=response_data)


@api.route("/clients/<caseref>/reports/<id>/supportingdocuments", methods=["POST"])
def handle_supporting_docs(caseref, id):
    data = validate_request_data(request, get_request_details_for_logs(), caseref)

    response_data, response_status = supporting_docs.endpoint_handler(
        data=data, caseref=caseref, id=id
    )

    if response_status in [201, 200]:
        logger.info(
            response_data, extra=get_request_details_for_logs(status=response_status)
        )
        return jsonify(response_data), response_status
    else:
        logger.error(
            response_data, extra=get_request_details_for_logs(status=response_status)
        )
        abort(response_status, description=response_data)


@api.route("/clients/<caseref>/reports/<id>/checklists/<checklistId>", methods=["PUT"])
@api.route("/clients/<caseref>/reports/<id>/checklists", methods=["POST"])
def handle_checklists(caseref, id, checklistId=None):
    data = validate_request_data(request, get_request_details_for_logs(), caseref)

    response_data, response_status = checklists.endpoint_handler(
        data=data,
        caseref=caseref,
        id=id,
        checklist_id=checklistId,
        method=request.method,
    )

    if response_status in [201, 200]:
        logger.info(
            response_data, extra=get_request_details_for_logs(status=response_status)
        )
        return jsonify(response_data), response_status
    else:
        logger.error(
            response_data, extra=get_request_details_for_logs(status=response_status)
        )
        abort(response_status, description=response_data)


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
