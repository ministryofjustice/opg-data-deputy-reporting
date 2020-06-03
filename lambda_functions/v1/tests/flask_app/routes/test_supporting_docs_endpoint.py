import json

import pytest
import requests
from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.tests.flask_app.routes import cases_supporting_docs_endpoint


@pytest.mark.run(order=1)
@pytest.mark.usefixtures(
    "patched_get_secret",
    "patched_submit_document_to_sirius",
    "patched_send_get_to_sirius",
)
@cases_data(module=cases_supporting_docs_endpoint)
def test_supporting_docs(server, case_data: CaseDataGetter):
    (
        test_data,
        test_headers,
        test_report_id,
        test_case_ref,
        expected_response_status_code,
        expected_response_data,
    ) = case_data.get()

    with server.app_context():

        print(f"test_case_ref: {test_case_ref}")
        print(f"test_report_id: {test_report_id}")

        r = requests.post(
            f"{server.url}/clients/{test_case_ref}/reports/"
            f"{test_report_id}/supportingdocuments",
            headers=test_headers,
            data=json.dumps(test_data),
        )

        assert r.status_code == expected_response_status_code
        assert r.json() == expected_response_data
