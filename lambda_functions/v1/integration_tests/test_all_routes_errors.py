import pytest

from lambda_functions.v1.integration_tests.conftest import (
    send_a_request,
    configs_to_test,
)


@pytest.mark.smoke_test
@pytest.mark.run(order=10)
@pytest.mark.parametrize("test_config", configs_to_test)
def test_403(test_config, monkeypatch):
    print(f"Using test_config: {test_config['name']}")

    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "not_real")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "not_real")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "not_real")

    routes = [
        {
            "route": f"/clients/{test_config['case_ref']}/reports",
            "method": "POST",
            "payload": {},
        },
        {
            "route": f"/clients/{test_config['case_ref']}/reports/"
            f"{test_config['report_id']}/supportingdocuments",
            "method": "POST",
            "payload": {},
        },
        {
            "route": f"/clients/{test_config['case_ref']}/reports/"
            f"{test_config['report_id']}/checklists",
            "method": f"POST",
            "payload": {},
        },
        {
            "route": f"/clients/{test_config['case_ref']}/reports/"
            f"{test_config['report_id']}/checklists/"
            f"{test_config['checklist_id']}",
            "method": "PUT",
            "payload": {},
        },
    ]

    for route in routes:

        url = f"{test_config['url']}/{route['route']}"
        status, response = send_a_request(
            url=url,
            method=route["method"],
            payload=route["payload"],
            test_config=test_config,
        )

        assert status == 403
