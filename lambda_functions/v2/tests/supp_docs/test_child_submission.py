import pytest

from lambda_functions.v2.functions.documents.app.api.supporting_docs import (
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
    case_ref = 1111
    report_id = "695bcfae-e2a4-4805-90de-4a814e8d49d2"

    test_data = {
        "supporting_document": {
            "data": {
                "type": "supportingdocuments",
                "attributes": {"submission_id": submission_id},
                "file": {
                    "name": "Report_1234567T_2018_2019_11111.pdf",
                    "mimetype": "application/pdf",
                    "source": "string",
                },
            }
        }
    }

    result = determine_document_parent_id(
        data=test_data, case_ref=case_ref, report_id=report_id
    )

    assert result == expected_response
