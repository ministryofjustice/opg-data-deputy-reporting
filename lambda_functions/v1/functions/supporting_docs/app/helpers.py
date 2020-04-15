# Helpers
import os


def compare_two_dicts(required_structure, test_dict, path="", missing=[]):

    for key in required_structure:
        if key not in test_dict:
            missing_item = f"{path}->{key}"
            if missing_item not in missing:
                missing.append(missing_item)
        else:
            if type(required_structure[key]) is dict:
                if path == "":
                    path = key
                else:
                    path = path + "->" + key
                compare_two_dicts(
                    required_structure[key], test_dict[key], path, missing
                )
            else:
                if isinstance(test_dict[key], type(None)):
                    missing.append(f"{path}->{key}")
                elif type(test_dict[key]) == str and len(test_dict[key]) == 0:
                    missing_item = f"{path}->{key}"

                    if missing_item not in missing:
                        missing.append(missing_item)

    return missing


def format_response_message(uuid, caseref, type, submission_id):

    base_url = os.environ["BASE_URL"]
    response = {
        "data": {
            "type": type,
            "id": uuid,
            "attributes": {"submission_id": submission_id},
            "links": {
                "self": f"{base_url}/reports/{uuid}",
                "client": f"{base_url}/clients/{caseref}",
            },
        }
    }

    return response
