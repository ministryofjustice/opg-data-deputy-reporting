import base64
import os

import boto3
import pytest
from moto import mock_s3

from lambda_functions.v2.functions.documents.app.api.helpers import (
    get_encoded_s3_object,
)

"""
Tests to add:

* get file by key
* try to get file but bucket doesn't exist
* try to get file but key doesn't exist
* try to get file but encoding breaks
try to get file but saving locally fails
try to get file but opening locally fails
"""


@pytest.mark.parametrize(
    "test_bucket, test_key, expected_result",
    [("valid_bucket", "test_file_on_aws.txt", "overwritten by test")],
)
def test_get_encoded_s3_object(test_bucket, test_key, expected_result):
    path_to_current_file = os.path.realpath(__file__)
    current_directory = os.path.split(path_to_current_file)[0]
    test_file = os.path.join(current_directory, "test_file.txt")

    with open(test_file, "rb") as image_file:
        expected_result = base64.b64encode(image_file.read()).decode("utf-8")

    with mock_s3():
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="valid_bucket")
        s3_client.upload_file(test_file, "valid_bucket", "test_file_on_aws.txt")

        result = get_encoded_s3_object(
            s3_client=s3_client, bucket=test_bucket, key=test_key
        )
        print(f"result: {result}")
        assert result == expected_result


@pytest.mark.parametrize(
    "test_bucket, test_key, expected_result",
    [
        ("invalid_bucket", "test_file_on_aws.txt", None),
        ("valid_bucket", "not_a_file_on_aws.txt", None),
    ],
)
def test_get_encoded_s3_object_error(test_bucket, test_key, expected_result):
    path_to_current_file = os.path.realpath(__file__)
    current_directory = os.path.split(path_to_current_file)[0]
    test_file = os.path.join(current_directory, "test_file.txt")

    with mock_s3():
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="valid_bucket")
        s3_client.upload_file(test_file, "valid_bucket", "test_file_on_aws.txt")

        result = get_encoded_s3_object(
            s3_client=s3_client, bucket=test_bucket, key=test_key
        )
        print(f"result: {result}")
        assert result == expected_result
