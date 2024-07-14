import sys


def parse_data_to_json(input_text, sentences, triplets, mappings):
    data = {
        "input": input_text,
        "preprocess": {
            "header": "Preprocessed Sentences",
            "output": [],
        },
        "extract": {
            "header": "Extracted Triplets",
            "output": [],
        },
        "suggest": {
            "header": "Countermeasure Suggestions",
            "output": [],
        },
    }

    data["preprocess"]["output"] = sentences

    triplets_data = []
    for token in triplets:
        triplets_str = ""
        for action in token:
            subjects = [tok.text for tok in token[action]["subjects"]]
            if len(subjects) == 0:
                subjects = ["_"]
            act = token[action]["action"].text
            if token[action]["negated"]:
                act = "not " + act
            if act == "":
                act = "_"
            objects = [tok.text for tok in token[action]["objects"]]
            if len(objects) == 0:
                objects = ["_"]

            subs = "|".join(subjects)
            objs = "|".join(objects)

            triplets_str += f"{subs} -> {act} -> {objs}\n\n"
        triplets_data.append(triplets_str.strip())

    data["extract"]["output"] = triplets_data

    mapping_data = []
    for mapping in mappings:
        mapping_str = ""
        for sugg in mapping:
            act = sugg["action"]
            objects = sugg["objects"]
            if objects is None or len(objects) == 0:
                objects = ["_"]
            objs = "|".join(objects)
            mapping_str += f"{act} -> {objs}\n\n"
        mapping_data.append(mapping_str.strip())

    data["suggest"]["output"] = mapping_data

    return data
