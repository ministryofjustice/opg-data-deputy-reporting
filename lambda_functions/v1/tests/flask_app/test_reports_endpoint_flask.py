import json


from lambda_functions.v1.flask_app.app.api import reports

from lambda_functions.v1.tests.helpers.use_test_data import is_valid_schema


def test_endpoint_handler_valid_event(
    patched_requests_flask,
    patched_get_secret,
    default_request_case_ref,
    default_report_request_body_flask,
):

    result_data, result_status_code = reports.endpoint_handler(
        data=default_report_request_body_flask, caseref=default_request_case_ref,
    )

    assert result_status_code == 201
    assert is_valid_schema(json.loads(result_data), "201_created_schema.json")


#
#
# def test_lambda_handler_invalid_event(
#     patched_requests,
#     patched_get_secret,
#     patched_validate_event_fail,
#     default_request_case_ref,
#     default_report_request_body,
# ):
#     path_params = {"caseref": default_request_case_ref}
#     event = build_aws_event(
#         event_body=json.dumps(default_report_request_body),
#         event_path_parementers=path_params,
#         as_json=False,
#     )
#
#     context = None
#
#     result = lambda_handler(event=event, context=context)
#
#
#     assert is_valid_schema(result, "standard_lambda_response_schema.json")
#     assert result["statusCode"] == 400
#
#
# @cases_data(module=reports_endpoint_test_cases)
# def test_validate_payload(case_data: CaseDataGetter):
#     body, case_ref, expected_result = case_data.get()
#     path_params = {"caseref": case_ref}
#     event = build_aws_event(
#         event_body=json.dumps(body), event_path_parementers=path_params, as_json=False
#     )
#
#     valid_event, errors = validate_event(event)
#
#     assert valid_event == expected_result[0]
#     assert sorted(errors) == sorted(expected_result[1])
#
#
# def test_transform_event_to_sirius_request(
#     default_report_request_body,
#     default_request_case_ref,
#     default_sirius_reports_request,
# ):
#     path_params = {"caseref": default_request_case_ref}
#     event = build_aws_event(
#         event_body=json.dumps(default_report_request_body),
#         event_path_parementers=path_params,
#         as_json=False,
#     )
#
#     payload = transform_event_to_sirius_request(event)
#
#     assert is_valid_schema(json.loads(payload),
#     "sirius_documents_payload_schema.json")
#     assert payload == json.dumps(default_sirius_reports_request)
#
#
# def test_sirius_request_has_and_submission_id(
#     default_report_request_body,
#     default_request_case_ref,
#     default_sirius_reports_request,
# ):
#     path_params = {"caseref": default_request_case_ref}
#     event = build_aws_event(
#         event_body=json.dumps(default_report_request_body),
#         event_path_parementers=path_params,
#         as_json=False,
#     )
#
#     payload = transform_event_to_sirius_request(event)
#
#     assert json.loads(payload)["metadata"]["submission_id"]
