from pytest_cases import case_name, CaseData, case_tags


@case_tags("success")
@case_name("Sirius responds with 200")
def case_200() -> CaseData:

    sirius_response_code = 200
    sirius_response = {
        "type": "Report - General",
        "filename": "Report_1234567T_2018_2019_11111.pdf",
        "mimetype": "application/pdf",
        "metadata": {"submission_id": 123},
        "uuid": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
        "parentUuid": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
    }

    api_response_code = 200
    api_response = {
        "data": {
            "type": "Report - General",
            "id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            "attributes": {
                "submission_id": 123,
                "parent_id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            },
        }
    }

    return (sirius_response_code, sirius_response, api_response_code, api_response)


@case_tags("success")
@case_name("Sirius responds with 200 - no parent id")
def case_200_no_parents() -> CaseData:

    sirius_response_code = 200
    sirius_response = {
        "type": "Report - General",
        "filename": "Report_1234567T_2018_2019_11111.pdf",
        "mimetype": "application/pdf",
        "metadata": {"submission_id": 123},
        "uuid": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
    }

    api_response_code = 200
    api_response = {
        "data": {
            "type": "Report - General",
            "id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            "attributes": {"submission_id": 123, "parent_id": None},
        }
    }

    return (sirius_response_code, sirius_response, api_response_code, api_response)


@case_tags("success")
@case_name("Sirius responds with 201")
def case_201() -> CaseData:

    sirius_response_code = 201
    sirius_response = {
        "type": "Report - General",
        "filename": "Report_1234567T_2018_2019_11111.pdf",
        "mimetype": "application/pdf",
        "metadata": {"submission_id": 123},
        "uuid": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
        "parentUuid": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
    }

    api_response_code = 201
    api_response = {
        "data": {
            "type": "Report - General",
            "id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            "attributes": {
                "submission_id": 123,
                "parent_id": "5a8b1a26-8296-4373-ae61-f8d0b250e773",
            },
        }
    }

    return (sirius_response_code, sirius_response, api_response_code, api_response)


#  TODO needs moving into new_submit_document_to_sirius test
# @case_tags("error")
# @case_name("Sirius responds with 404 (bad url params)")
# def case_404_url_params() -> CaseData:
#
#     sirius_response_code = 404
#     sirius_response = "it really doesn't matter what sirius thinks here"

#     api_response_code = 400
#     api_response = {"message": "URL params not right"}
#
#     return (sirius_response_code, sirius_response, api_response_code, api_response)


@case_tags("error")
@case_name("Sirius responds with a code, message and details")
def case_all() -> CaseData:

    sirius_response_code = 400
    sirius_response = "spurious sirius error message"
    error_details = "here's some more details"

    api_response_code = 400
    api_response = "spurious sirius error message"

    return (
        sirius_response_code,
        sirius_response,
        error_details,
        api_response_code,
        api_response,
    )


@case_tags("error")
@case_name("Sirius responds with a message and details")
def case_code_missing() -> CaseData:

    sirius_response_code = None
    sirius_response = "spurious sirius error message"
    error_details = "here's some more details"

    api_response_code = 500
    api_response = "spurious sirius error message"

    return (
        sirius_response_code,
        sirius_response,
        error_details,
        api_response_code,
        api_response,
    )


@case_tags("error")
@case_name("Sirius responds with a code and details")
def case_message_missing() -> CaseData:

    sirius_response_code = 400
    sirius_response = None
    error_details = "here's some more details"

    api_response_code = 400
    api_response = "here's some more details"

    return (
        sirius_response_code,
        sirius_response,
        error_details,
        api_response_code,
        api_response,
    )


@case_tags("error")
@case_name("Sirius responds with a code, message")
def case_missing_details() -> CaseData:

    sirius_response_code = 400
    sirius_response = "spurious sirius error message"
    error_details = None

    api_response_code = 400
    api_response = "spurious sirius error message"

    return (
        sirius_response_code,
        sirius_response,
        error_details,
        api_response_code,
        api_response,
    )


@case_tags("error")
@case_name("Sirius responds with a code, message, empty details")
def case_empty_details() -> CaseData:

    sirius_response_code = 400
    sirius_response = "spurious sirius error message"
    error_details = ""

    api_response_code = 400
    api_response = "spurious sirius error message"

    return (
        sirius_response_code,
        sirius_response,
        error_details,
        api_response_code,
        api_response,
    )


@case_tags("error")
@case_name("Sirius responds with details no validation errors")
def case_details_no_validation() -> CaseData:

    sirius_response_code = 400
    sirius_response = {"detail": "some detail in sirius response"}
    error_details = "here's some more details"

    api_response_code = 400
    api_response = "some detail in sirius response"

    return (
        sirius_response_code,
        sirius_response,
        error_details,
        api_response_code,
        api_response,
    )


@case_tags("error")
@case_name("Sirius responds with details and validation errors")
def case_details_validation() -> CaseData:

    sirius_response_code = 400
    sirius_response = {
        "detail": "some detail in sirius response",
        "validation_errors": "some validation error",
    }
    error_details = "here's some more details"

    api_response_code = 400
    api_response = "some detail in sirius response - some validation error"

    return (
        sirius_response_code,
        sirius_response,
        error_details,
        api_response_code,
        api_response,
    )
