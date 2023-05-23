import requests
import json


payload = {
    "report": {
        "data": {
            "type": "reports",
            "attributes": {
                "submission_id": 12345,
                "reporting_period_from": "2019-01-01",
                "reporting_period_to": "2019-12-31",
                "year": 2019,
                "date_submitted": "2020-01-03T09:30:00.001Z",
                "type": "PF",
            },
            "file": {
                "name": "s3program_probably_record.pdf",
                "mimetype": "application/pdf",
                "s3_reference": "dd_doc_62_15916290546271",
            },
        }
    }
}
body = json.dumps(payload)
headers = {
        "Content-Type": "application/json",
    }
url = "http://test.com"

response = requests.request("POST", url, data=body, headers=headers)

print(response.get_json())
