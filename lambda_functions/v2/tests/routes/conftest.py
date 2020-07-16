import json
import logging
import os
import socket
import sys
import threading
import time

import pytest
from flask import Flask

from lambda_functions.v2.functions.documents.app import api, create_app


class StreamToLogger(object):
    """
   Fake file-like stream object that redirects writes to a logger instance.
   Not actually used by tests, but if the tests fail the logger messages from the flask
   server thread are output to the out.log file, which is super handy
   """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
    filename="out.log",
    filemode="a",
)

stdout_logger = logging.getLogger("STDOUT")
sl = StreamToLogger(stdout_logger, logging.INFO)
sys.stdout = sl

stderr_logger = logging.getLogger("STDERR")
sl = StreamToLogger(stderr_logger, logging.ERROR)
sys.stderr = sl


def get_open_port():
    """ Find free port on a local system """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def wait_until(predicate, timeout=5, interval=0.05, *args, **kwargs):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if predicate(*args, **kwargs):
            return True
        time.sleep(interval)
    return False


@pytest.fixture(scope="session")
def server():

    version = os.environ.get("API_VERSION")
    print(f"version: {version}")

    http_server = create_app(Flask)
    routes = [str(p) for p in http_server.url_map.iter_rules()]
    print(f"routes: {routes}")

    port = get_open_port()
    http_server.url = "http://localhost:{}/{}/flask".format(port, version)
    print(f"http_server.url: {http_server.url}")

    def start():
        print("start server")
        http_server.run(port=port)

    p = threading.Thread(target=start)
    p.daemon = True
    p.start()

    def check():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("localhost", port))
            return True
        except Exception:
            return False
        finally:
            s.close()

    rc = wait_until(check)
    assert rc, "failed to start service"

    yield http_server

    p.join(timeout=0.5)


@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"
    os.environ["AWS_XRAY_CONTEXT_MISSING"] = "LOG_ERROR"


@pytest.fixture(autouse=True)
def patched_get_secret(monkeypatch):
    def mock_secret(*args, **kwargs):
        print("I AM A FAKE SECRET")
        return "this_is_a_secret_string"

    monkeypatch.setattr(api.sirius_service, "get_secret", mock_secret)


valid_case_refs = ["1111", "2222", "3333"]


@pytest.fixture(autouse=True)
def patched_submit_document_to_sirius(monkeypatch):
    def mock_submit_document_to_sirius(*args, **kwargs):
        print("FAKE POST TO SIRIUS")

        data = json.loads(kwargs["data"])
        case_ref = data["caseRecNumber"]
        print(f"case_ref: {type(case_ref)}")

        if case_ref in valid_case_refs:
            response_code = 201
            response_data = {"uuid": "5a8b1a26-8296-4373-ae61-f8d0b250e773"}
        else:
            response_code = 404
            response_data = None

        print(f"(response_code, response_data): {(response_code, response_data)}")
        return (response_code, response_data)

    monkeypatch.setattr(
        api.sirius_service, "submit_document_to_sirius", mock_submit_document_to_sirius
    )


@pytest.fixture(autouse=True)
def patched_send_get_to_sirius(monkeypatch):
    def mock_send_get_to_sirius(*args, **kwargs):
        print("FAKE GET TO SIRIUS")
        return None

    monkeypatch.setattr(
        api.sirius_service, "send_get_to_sirius", mock_send_get_to_sirius
    )


@pytest.fixture(autouse=True)
def patched_send_get_to_sirius_healthcheck(monkeypatch):
    def mock_send_get_to_sirius(*args, **kwargs):
        print("FAKE GET TO SIRIUS")
        return 200, "OK"

    monkeypatch.setattr(
        api.sirius_service, "send_get_to_sirius", mock_send_get_to_sirius
    )
