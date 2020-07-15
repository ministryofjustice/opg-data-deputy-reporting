import pytest

from lambda_functions.v1.functions.flask_app.app import api

from lambda_functions.v1.functions.flask_app.app.api.helpers import handle_file_source

"""
Tests to add:

* file is sent
* s3 ref is sent
neither file or s3 is sent
both file and s3 are sent
DIGIDEPS_S3_BUCKET is not set
get_encoded_s3_object fails
get_digideps_s3_client fails
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
