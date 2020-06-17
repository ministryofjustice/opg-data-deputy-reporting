import json
import os
from json import JSONDecodeError

import pytest
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.integration_tests import cases_payload_errors
from lambda_functions.v1.integration_tests.conftest import configs_to_test
from lambda_functions.v1.integration_tests.conftest import send_a_request


def all_routes(case_ref, report_id, checklist_id):
    return [
        {"route": f"/clients/{case_ref}/reports", "method": "POST"},
        {
            "route": f"/clients/{case_ref}/reports/{report_id}/supportingdocuments",
            "method": "POST",
        },
        {
            "route": f"/clients/{case_ref}/reports/{report_id}/checklists",
            "method": "POST",
        },
        {
            "route": f"/clients/{case_ref}/reports/"
            f"{report_id}/checklists/"
            f"{checklist_id}",
            "method": "PUT",
        },
    ]


@pytest.mark.xfail(
    raises=AssertionError, reason="error code should be 'OPGDATA-API-FORBIDDEN'"
)
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_403(test_config, monkeypatch):
    print(f"Using test_config: {test_config['name']}")

    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "not_real")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "not_real")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "not_real")

    routes = all_routes(
        case_ref=test_config["case_ref"],
        report_id=test_config["report_id"],
        checklist_id=test_config["checklist_id"],
    )

    payload = {}

    for route in routes:
        print(f"route: {route}")

        url = f"{test_config['url']}/{route['route']}"
        status, response = send_a_request(
            url=url, method=route["method"], payload=payload, test_config=test_config,
        )

        assert status == 403
        response_data = json.loads(response)
        assert response_data["errors"]["code"] == "OPGDATA-API-FORBIDDEN"


@pytest.mark.xfail(
    raises=(AssertionError, JSONDecodeError),
    reason="error code should be " "'OPGDATA-API-INVALIDREQUEST'",
)
@pytest.mark.skipif(os.getenv("AWS_SESSION_TOKEN") == "", reason="AWS creds not set")
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_400_bad_url_params(test_config):
    print(f"Using test_config: {test_config['name']}")
    # this actually returns "unable to parse" error from lambda payload validation,
    # not from API-G??

    routes = []
    routes.extend(
        all_routes(
            case_ref="not_a_real_caseref",
            report_id=test_config["report_id"],
            checklist_id=test_config["checklist_id"],
        )
    )
    routes.extend(
        all_routes(
            case_ref=test_config["case_ref"],
            report_id="not_a_report_id",
            checklist_id=test_config["checklist_id"],
        )
    )
    routes.extend(
        all_routes(
            case_ref=test_config["case_ref"],
            report_id=test_config["report_id"],
            checklist_id="not_a_checklist_id",
        )
    )

    payload = {}

    for route in routes:
        print(f"route: {route}")
        url = f"{test_config['url']}/{route['route']}"
        status, response = send_a_request(
            url=url, method=route["method"], payload=payload, test_config=test_config,
        )
        print(f"status: {status}")
        print(f"response: {response}")

        assert status == 400
        response_data = json.loads(response)
        assert response_data["errors"]["code"] == "OPGDATA-API-INVALIDREQUEST"


@pytest.mark.skipif(os.getenv("AWS_SESSION_TOKEN") == "", reason="AWS creds not set")
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_404(test_config):
    # print(f"Using test_config: {test_config['name']}")

    route = "not_a_real_endpoint"
    payload = {}

    url = f"{test_config['url']}/{route}"
    status, response = send_a_request(
        url=url, method="POST", payload=payload, test_config=test_config,
    )

    assert status == 404
    response_data = json.loads(response)
    assert response_data["errors"]["code"] == "OPGDATA-API-NOTFOUND"


@pytest.mark.xfail(raises=AssertionError, reason="405 error not implemented'")
@pytest.mark.skipif(os.getenv("AWS_SESSION_TOKEN") == "", reason="AWS creds not set")
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_405(test_config):
    print(f"Using test_config: {test_config['name']}")

    routes = all_routes(
        case_ref=test_config["case_ref"],
        report_id=test_config["report_id"],
        checklist_id=test_config["checklist_id"],
    )

    payload = {}

    for route in routes:
        if route["method"] in ["POST", "PUT"]:
            method = "GET"
        else:
            method = "POST"

        url = f"{test_config['url']}/{route['route']}"
        status, response = send_a_request(
            url=url, method=method, payload=payload, test_config=test_config,
        )
        print(f"route: {route} - {status}")
        assert status == 405
        response_data = json.loads(response)
        assert response_data["errors"]["code"] == "OPGDATA-API-NOTALLOWED"


@pytest.mark.xfail(raises=AssertionError, reason="Custom headers not implemented'")
@pytest.mark.skipif(os.getenv("AWS_SESSION_TOKEN") == "", reason="AWS creds not set")
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_500(test_config,):
    print(f"Using test_config: {test_config['name']}")

    routes = all_routes(
        case_ref=test_config["case_ref"],
        report_id=test_config["report_id"],
        checklist_id=test_config["checklist_id"],
    )

    payload = {}

    for route in routes:

        headers = [{"header_name": "X-Error-Response", "header_value": "500"}]

        url = f"{test_config['url']}/{route['route']}"
        status, response = send_a_request(
            url=url,
            method=route["method"],
            payload=payload,
            test_config=test_config,
            extra_headers=headers,
        )
        print(f"route: {route} - {status}")
        assert status == 500
        response_data = json.loads(response)
        assert response_data["errors"]["code"] == "OPGDATA-API-SERVERERROR"


@pytest.mark.xfail(raises=AssertionError, reason="Custom headers not implemented'")
@pytest.mark.skipif(os.getenv("AWS_SESSION_TOKEN") == "", reason="AWS creds not set")
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_503(test_config,):
    print(f"Using test_config: {test_config['name']}")

    routes = all_routes(
        case_ref=test_config["case_ref"],
        report_id=test_config["report_id"],
        checklist_id=test_config["checklist_id"],
    )

    payload = {}

    for route in routes:

        headers = [{"header_name": "X-Error-Response", "header_value": "503"}]

        url = f"{test_config['url']}/{route['route']}"
        status, response = send_a_request(
            url=url,
            method=route["method"],
            payload=payload,
            test_config=test_config,
            extra_headers=headers,
        )
        print(f"route: {route} - {status}")
        assert status == 500
        response_data = json.loads(response)
        assert response_data["errors"]["code"] == "OPGDATA-API-UNAVAILABLE"


@pytest.mark.xfail(
    raises=(AssertionError, JSONDecodeError),
    reason="Not all required fields are " "validated by API Gateway'",
)
@pytest.mark.skipif(os.getenv("AWS_SESSION_TOKEN") == "", reason="AWS creds not set")
@pytest.mark.smoke_test
@pytest.mark.run(order=1)
@pytest.mark.parametrize("test_config", configs_to_test)
@cases_data(module=cases_payload_errors)
def test_bad_payload(case_data: CaseDataGetter, test_config):
    (url, method, payload, expected_status_code) = case_data.get(test_config)

    status, response = send_a_request(
        url=url, method=method, payload=payload, test_config=test_config
    )

    print(f"response: {response}")

    assert status == expected_status_code
    response_data = json.loads(response)
    for error in response_data["errors"]:
        assert error["code"] == "OPGDATA-API-INVALIDREQUEST"
