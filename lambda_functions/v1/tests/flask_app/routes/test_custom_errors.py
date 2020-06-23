import pytest
import requests
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.tests.flask_app.routes import cases_custom_endpoint_errors


@pytest.mark.run(order=1)
@pytest.mark.usefixtures(
    "patched_get_secret",
    "patched_submit_document_to_sirius",
    "patched_send_get_to_sirius",
)
@cases_data(module=cases_custom_endpoint_errors, has_tag="endpoint")
def test_custom_errors(server, case_data: CaseDataGetter):
    (
        test_url,
        test_headers,
        test_data,
        test_method,
        expected_response_status_code,
        expected_response_data,
    ) = case_data.get()

    test_url = test_url["url"]

    with server.app_context():

        if test_method == "NOT POST":
            r = requests.get(url=f"{server.url}/{test_url}")
        elif test_method == "PUT":
            data = test_data

            r = requests.put(
                f"{server.url}/clients/{test_url}", headers=test_headers, data=data,
            )
        else:

            data = test_data

            r = requests.post(
                f"{server.url}/clients/{test_url}", headers=test_headers, data=data,
            )

        print(f"r.text: {r.text}")

        assert r.status_code == expected_response_status_code
        assert r.json()["body"]["error"]["code"] == expected_response_data
