import requests
import os


def lambda_handler():

    api_host = os.environ["BASE_URL"]

    print("API URL: " + api_host)

    r = requests.get(api_host + "/api/health-check/service-status", verify=False)

    response = {
        "statusCode": r.status_code,
        "headers": {"myheader": "response"},
        "body": r.text,
    }

    return response