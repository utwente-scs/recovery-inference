import json

def load_mapping(file_path):
    with open(file_path, "r") as file:
        mapping = json.load(file)
    return mapping


def map_to_recovery_from_triplets(triplets, mapping_path):
    mapping = load_mapping(mapping_path)
    mappings = []
    for triplet in triplets:
        subjs = triplet["subjects"]
        act = triplet["action"]
        neg = triplet["negated"]
        objs = triplet["objects"]
        pair = {"action": None, "objects": None}
        if act.lemma_ in mapping:
            if not neg:
                pair["action"] = mapping[act.lemma_]
                pair["objects"] = [obj.text for obj in objs]
        mappings.append(pair)
    return mappings
