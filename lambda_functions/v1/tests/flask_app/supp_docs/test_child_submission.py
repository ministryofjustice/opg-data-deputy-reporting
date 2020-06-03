import pytest


from lambda_functions.v1.functions.flask_app.app.api.sirius_service import (
    build_sirius_url,
)
from lambda_functions.v1.functions.flask_app.app.api.supporting_docs import (
    determine_document_parent_id,
)


@pytest.mark.parametrize(
    "submission_id, expected_response",
    [
        ("11111", None),
        ("22222", "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0"),
        ("55555", "e8c14b7f-d0fc-4820-9ac7-58d61d4160d0"),
        ("88888", None),
    ],
)
def test_determine_document_parent_id(
    patched_send_get_to_sirius, submission_id, expected_response
):
    url = build_sirius_url(
        base_url="https://www.notanurl.com",
        version="1",
        endpoint="pretend",
        url_params={"metadata[submission_id]": submission_id},
    )

    result = determine_document_parent_id(url)

    assert result == expected_response
