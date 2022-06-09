import pytest
import requests


@pytest.mark.run(order=1)
@pytest.mark.usefixtures(
    "patched_get_secret",
    "patched_send_get_to_sirius_healthcheck",
)
def test_healthcheck(server):
    with server.app_context():
        r = requests.get(
            f"{server.url}/healthcheck", headers={"Content-Type": "application/json"}
        )

        print(f"r.text: {r.text}")

        assert r.status_code == 200
        assert r.json() == "OK"


@pytest.mark.run(order=1)
def test_reporting_healthcheck(server):
    with server.app_context():
        r = requests.get(
            f"{server.url}/reporting_healthcheck",
            headers={"Content-Type": "application/json"},
        )

        print(f"r.text: {r.text}")

        assert r.status_code == 200
        assert r.json() == "OK"
