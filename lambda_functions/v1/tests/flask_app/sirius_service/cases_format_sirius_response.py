from pytest_cases import case_name, CaseData


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


@case_name("Sirius responds with 404 (bad url params)")
def case_404_url_params() -> CaseData:

    sirius_response_code = 404
    sirius_response = "it really doesn't matter what sirius thinks here"

    # TODO check - I think this is currently a 404 so may need to change this?
    # TODO this error message is rubbish
    api_response_code = 400
    api_response = {"message": "URL params not right"}

    return (sirius_response_code, sirius_response, api_response_code, api_response)


@case_name("Sirius responds with 400")
def case_400() -> CaseData:

    sirius_response_code = 400
    sirius_response = "spurious sirius error message"

    # TODO this error message should be in the format {"message": "blah"} to match
    #  the other custom Sirius errors
    api_response_code = 400
    api_response = "sirius problem: 400 - spurious sirius error message"

    return (sirius_response_code, sirius_response, api_response_code, api_response)


@case_name("Sirius responds with 500")
def case_500() -> CaseData:

    sirius_response_code = 500
    sirius_response = "something has gone terribly wrong"

    # TODO this error message should be in the format {"message": "blah"} to match
    #  the other custom Sirius errors
    api_response_code = 500
    api_response = "sirius problem: 500 - something has gone terribly wrong"

    return (sirius_response_code, sirius_response, api_response_code, api_response)


@case_name("Sirius call does something unexpected")
def case_500_exception() -> CaseData:

    sirius_response_code = 200
    sirius_response = "the data sirius has returned is all wrong"

    # TODO this error message should be in the format {"message": "blah"} to match
    #  the other custom Sirius errors
    api_response_code = 500
    api_response = "sirius problem: 500 - the data sirius has returned is all wrong"

    return (sirius_response_code, sirius_response, api_response_code, api_response)
