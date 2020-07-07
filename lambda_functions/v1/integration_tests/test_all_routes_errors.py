import copy
import json
import os
from json import JSONDecodeError

import pytest
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.integration_tests import cases_payload_errors
from lambda_functions.v1.integration_tests.conftest import (
    configs_to_test,
    generate_file_name,
)
from lambda_functions.v1.integration_tests.conftest import send_a_request

default_report_payload = {
    "report": {
        "data": {
            "type": "reports",
            "attributes": {
                "submission_id": 1234,
                "reporting_period_from": "2019-01-01",
                "reporting_period_to": "2019-12-31",
                "year": 2019,
                "date_submitted": "2020-01-03T09:30:00.001Z",
                "type": "PF",
            },
            "file": {
                "name": f"{generate_file_name()}.pdf",
                "mimetype": "application/pdf",
                "source": "string",
            },
        }
    }
}

default_supdocs_payload = {
    "supporting_document": {
        "data": {
            "type": "supportingdocuments",
            "attributes": {"submission_id": 1234},
            "file": {
                "name": f"{generate_file_name()}.pdf",
                "mimetype": "application/pdf",
                "source": "string",
            },
        }
    }
}

default_checklist_payload = {
    "checklist": {
        "data": {
            "type": "supportingdocuments",
            "attributes": {"submission_id": 1234},
            "file": {
                "name": f"{generate_file_name()}.pdf",
                "mimetype": "application/pdf",
                "source": "string",
            },
        }
    }
}


def all_routes(case_ref, report_id, checklist_id):

    return_values = [
        {
            "route": f"clients/{case_ref}/reports/"
            f"{report_id}/checklists/"
            f"{checklist_id}",
            "method": "PUT",
            "payload": copy.deepcopy(default_checklist_payload),
        }
    ]
    if "not_a_" in report_id:
        return_values.append(
            {
                "route": f"clients/{case_ref}/reports/{report_id}/supportingdocuments",
                "method": "POST",
                "payload": copy.deepcopy(default_supdocs_payload),
            }
        )
        return_values.append(
            {
                "route": f"/lients/{case_ref}/reports/{report_id}/checklists",
                "method": "POST",
                "payload": copy.deepcopy(default_checklist_payload),
            }
        )
    if "not_a_" in case_ref:
        return_values.append(
            {
                "route": f"clients/{case_ref}/reports",
                "method": "POST",
                "payload": copy.deepcopy(default_report_payload),
            }
        )

    return return_values


@pytest.mark.xfail(
    reason="Works differently now we're using creds from the environment"
)
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_403(test_config, monkeypatch):

    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "not_real")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "not_real")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "not_real")

    routes = all_routes(
        case_ref=test_config["case_ref"],
        report_id=test_config["report_id"],
        checklist_id=test_config["checklist_id"],
    )

    for route in routes:

        url = f"{test_config['url']}/{route['route']}"
        status, response = send_a_request(
            url=url,
            method=route["method"],
            payload=route["payload"],
            test_config=test_config,
        )

        assert status == 403
        response_data = json.loads(response)
        assert response_data["errors"]["code"] == "OPGDATA-API-INVALIDREQUEST"


@pytest.mark.xfail(reason="Is actually 404")
@pytest.mark.skipif(os.getenv("AWS_SESSION_TOKEN") == "", reason="AWS creds not set")
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_400_bad_url_params(test_config):

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

    for route in routes:

        url = f"{test_config['url']}/{route['route']}"

        status, response = send_a_request(
            url=url,
            method=route["method"],
            payload=route["payload"],
            test_config=test_config,
        )

        assert status == 400
        response_data = json.loads(response)

        # Need to also check its not payload error here as that gets checked first
        assert response_data["errors"]["code"] == "OPGDATA-API-INVALIDREQUEST"


@pytest.mark.skipif(os.getenv("AWS_SESSION_TOKEN") == "", reason="AWS creds not set")
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_404(test_config):

    route = "not_a_real_endpoint"
    payload = {}

    url = f"{test_config['url']}/{route}"
    status, response = send_a_request(
        url=url, method="POST", payload=payload, test_config=test_config,
    )

    assert status == 404
    response_data = json.loads(response)
    assert response_data["errors"]["code"] == "OPGDATA-API-NOTFOUND"


@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_405(test_config):

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

        assert status == 404
        response_data = json.loads(response)
        assert response_data["errors"]["code"] == "OPGDATA-API-NOTFOUND"


@pytest.mark.skip(reason="we need a file over 10mb")
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_413(test_config):

    with open("large_encoded_file.txt", "r") as large_file:

        payload = {
            "report": {
                "data": {
                    "type": "reports",
                    "attributes": {
                        "submission_id": 1234,
                        "reporting_period_from": "2019-01-01",
                        "reporting_period_to": "2019-12-31",
                        "year": 2019,
                        "date_submitted": "2020-01-03T09:30:00.001Z",
                        "type": "PF",
                    },
                    "file": {
                        "name": f"{generate_file_name()}.pdf",
                        "mimetype": "application/pdf",
                        "source": large_file.read(),
                    },
                }
            }
        }

        case_ref = test_config["case_ref"]
        route = f"/clients/{case_ref}/reports"
        url = f"{test_config['url']}/{route}"
        status, response = send_a_request(
            url=url, method="POST", payload=payload, test_config=test_config
        )

        assert status == 413
        response_data = json.loads(response)
        assert response_data["errors"]["code"] == "OPGDATA-API-FILESIZELIMIT"


@pytest.mark.xfail(raises=KeyError, reason="Badly formatted response'")
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_415(test_config, monkeypatch):

    routes = all_routes(
        case_ref=test_config["case_ref"],
        report_id=test_config["report_id"],
        checklist_id=test_config["checklist_id"],
    )

    for route in routes:

        url = f"{test_config['url']}/{route['route']}"
        status, response = send_a_request(
            url=url,
            method=route["method"],
            payload=route["payload"],
            test_config=test_config,
            content_type="application/zip",
        )
        assert status == 415
        response_data = json.loads(response)
        assert response_data["errors"]["code"] == "OPGDATA-API-MEDIA"


@pytest.mark.xfail(reason="Custom headers not implemented (yet)'")
@pytest.mark.skipif(os.getenv("AWS_SESSION_TOKEN") == "", reason="AWS creds not set")
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_500(test_config,):

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

        assert status == 500
        response_data = json.loads(response)
        assert response_data["errors"]["code"] == "OPGDATA-API-SERVERERROR"


@pytest.mark.xfail(reason="Custom headers not implemented (yet)'")
@pytest.mark.skipif(os.getenv("AWS_SESSION_TOKEN") == "", reason="AWS creds not set")
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_503(test_config,):

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

        assert status == 500
        response_data = json.loads(response)
        assert response_data["errors"]["code"] == "OPGDATA-API-UNAVAILABLE"


@pytest.mark.xfail(
    raises=(AssertionError, JSONDecodeError, TypeError),
    reason="Not all required fields are " "validated by API Gateway'",
)
@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
@cases_data(module=cases_payload_errors)
def test_bad_payload(case_data: CaseDataGetter, test_config):
    (url, method, payload, expected_status_code) = case_data.get(test_config)

    status, response = send_a_request(
        url=url, method=method, payload=payload, test_config=test_config
    )

    assert status == expected_status_code
    response_data = json.loads(response)
    if "errors" in response_data["body"]:
        for error in response_data["body"]["errors"]:
            assert error["code"] == "OPGDATA-API-INVALIDREQUEST"
    else:
        assert response_data["body"]["error"]["code"] == "OPGDATA-API-INVALIDREQUEST"
