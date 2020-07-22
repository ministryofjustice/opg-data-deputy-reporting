import pytest

from lambda_functions.v2.functions.documents.app import api
from lambda_functions.v2.functions.documents.app.api.helpers import handle_file_source

"""
Tests to add:

* file is sent
* s3 ref is sent
* neither file or s3 is sent FAILS
* both file and s3 are sent
* DIGIDEPS_S3_BUCKET is not set FAILS
* get_encoded_s3_object fails FAILS
* get_digideps_s3_client fails FAILS

can't think of any more, this is just a commit to test Circle CI
"""


@pytest.mark.parametrize(
    "test_dict, expected_result",
    [
        (
            {
                "name": "test_file_name",
                "type": "application/pdf",
                "s3_reference": "link_to_file",
            },
            "this is a base64 encoded file from s3",
        ),
        (
            {
                "name": "test_file_name",
                "type": "application/pdf",
                "source": "this is a base64 encoded file",
            },
            "this is a base64 encoded file",
        ),
        pytest.param(
            {"name": "test_file_name", "type": "application/pdf"},
            "this is a base64 encoded file from s3",
            marks=pytest.mark.xfail(reason="Not handled"),
        ),
        (
            {
                "name": "test_file_name",
                "type": "application/pdf",
                "s3_reference": "link_to_file",
                "source": "this is a base64 encoded file",
            },
            "this is a base64 encoded file",
        ),
    ],
)
def test_handle_file_source(monkeypatch, test_dict, expected_result):
    def mock_get_encoded_s3_object(*args, **kwwargs):
        print("mock_get_encoded_s3_object")
        return "this is a base64 encoded file from s3"

    monkeypatch.setattr(
        api.helpers, "get_encoded_s3_object", mock_get_encoded_s3_object
    )

    def mock_get_digideps_s3_client(*args, **kwargs):
        print("mock_get_digideps_s3_client")
        return "client"

    monkeypatch.setattr(
        api.helpers, "get_digideps_s3_client", mock_get_digideps_s3_client
    )

    monkeypatch.setenv("DIGIDEPS_S3_BUCKET", "secret")

    result = handle_file_source(test_dict)

    assert result == expected_result


@pytest.mark.xfail(reason="No error handling")
def test_env_var_not_set(monkeypatch):
    def mock_get_encoded_s3_object(*args, **kwwargs):
        print("mock_get_encoded_s3_object")
        return "this is a base64 encoded file from s3"

    monkeypatch.setattr(
        api.helpers, "get_encoded_s3_object", mock_get_encoded_s3_object
    )

    def mock_get_digideps_s3_client(*args, **kwargs):
        print("mock_get_digideps_s3_client")
        return "client"

    monkeypatch.setattr(
        api.helpers, "get_digideps_s3_client", mock_get_digideps_s3_client
    )

    test_dict = {
        "name": "test_file_name",
        "type": "application/pdf",
        "s3_reference": "link_to_file",
    }

    monkeypatch.delenv("DIGIDEPS_S3_BUCKET")

    result = handle_file_source(test_dict)

    assert result == "nice error handling ere"


@pytest.mark.xfail(reason="No error handling")
def test_get_encoded_s3_object_fails(monkeypatch):
    def mock_get_encoded_s3_object_fails(*args, **kwwargs):
        print("mock_get_encoded_s3_object")
        raise Exception

    monkeypatch.setattr(
        api.helpers, "get_encoded_s3_object", mock_get_encoded_s3_object_fails
    )

    def mock_get_digideps_s3_client(*args, **kwargs):
        print("mock_get_digideps_s3_client")
        return "client"

    monkeypatch.setattr(
        api.helpers, "get_digideps_s3_client", mock_get_digideps_s3_client
    )

    test_dict = {
        "name": "test_file_name",
        "type": "application/pdf",
        "s3_reference": "link_to_file",
    }

    monkeypatch.setenv("DIGIDEPS_S3_BUCKET", "secret")

    result = handle_file_source(test_dict)

    assert result == "nice error handling here"


@pytest.mark.xfail(reason="No error handling")
def test_get_digideps_s3_client_fails(monkeypatch):
    def mock_get_encoded_s3_object(*args, **kwwargs):
        print("mock_get_encoded_s3_object")
        return "this is a base64 encoded file from s3"

    monkeypatch.setattr(
        api.helpers, "get_encoded_s3_object", mock_get_encoded_s3_object
    )

    def mock_get_digideps_s3_client_fails(*args, **kwargs):
        print("mock_get_digideps_s3_client")
        raise Exception

    monkeypatch.setattr(
        api.helpers, "get_digideps_s3_client", mock_get_digideps_s3_client_fails
    )

    test_dict = {
        "name": "test_file_name",
        "type": "application/pdf",
        "s3_reference": "link_to_file",
    }

    monkeypatch.setenv("DIGIDEPS_S3_BUCKET", "secret")

    result = handle_file_source(test_dict)

    assert result == "nice error handling here"
