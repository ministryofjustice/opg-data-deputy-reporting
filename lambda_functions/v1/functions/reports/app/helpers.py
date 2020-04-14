# Helpers


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
