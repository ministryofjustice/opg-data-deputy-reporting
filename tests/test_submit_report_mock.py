import json
import os

import pytest
import requests

# from external_services.sirius_public_api import sirius_public_api_server
# from tests.external_services.sirius_public_api.sirius_public_api_server import \
#     MockServer
from tests.helpers.assertions import is_valid_uuid


@pytest.fixture(autouse=True)
def mock_env_setup(monkeypatch):
    monkeypatch.setenv("BASE_URL", "http://0.0.0.0:3333/api/public/v1/")
    monkeypatch.setenv("LOGGER_LEVEL", "DEBUG")

# @pytest.fixture(autouse=True)
# def mock_server(request):
#     server = MockServer()
#     server.start()
#     yield server
#     server.shutdown_server()


def test_mock_sirius_api_is_up():

    url = os.getenv("BASE_URL") + "documents"
    headers = {"Content-Type": "application/json"}
    body = {
        "caseRef": "0319392T",
        "direction": "DIRECTION_INCOMING",
        "documentSubType": "Report - General",
        "documentType": "Report - General",
        "file": {
            "fileName": "Report_1234567T_2018_2019_11111.pdf",
            "mimeType": "application/pdf",
            "source": "string",
        },
        "metaData": {},
    }

    r = requests.post(url=url, data=json.dumps(body), headers=headers)

    assert is_valid_uuid(r.json())
    assert r.status_code == 201
