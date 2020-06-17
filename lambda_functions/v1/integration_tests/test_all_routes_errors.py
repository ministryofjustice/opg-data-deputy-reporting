import pytest

from lambda_functions.v1.integration_tests.conftest import (
    send_a_request,
    configs_to_test,
)


def all_routes(case_ref, report_id, checklist_id):
    return [
        {"route": f"/clients/{case_ref}/reports", "method": "POST"},
        {
            "route": f"/clients/{case_ref}/reports/" f"{report_id}/supportingdocuments",
            "method": "POST",
        },
        {
            "route": f"/clients/{case_ref}/reports/" f"{report_id}/checklists",
            "method": f"POST",
        },
        {
            "route": f"/clients/{case_ref}/reports/"
            f"{report_id}/checklists/"
            f"{checklist_id}",
            "method": "PUT",
        },
    ]


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

        url = f"{test_config['url']}/{route['route']}"
        status, response = send_a_request(
            url=url, method=route["method"], payload=payload, test_config=test_config,
        )

        assert status == 403


@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_400_bad_caseref(test_config):
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
