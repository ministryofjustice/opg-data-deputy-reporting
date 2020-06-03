import pytest
import requests


@pytest.mark.run(order=1)
def test_healthcheck(server):
    with server.app_context():
        r = requests.get(
            f"{server.url}/healthcheck", headers={"Content-Type": "application/json"}
        )

        assert r.status_code == 200
        assert r.json() == "OK"
