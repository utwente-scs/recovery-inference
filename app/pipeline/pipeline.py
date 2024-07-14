from .preprocess import replace_IOCs, split_by_new_lines
from .extractor import *
from .mapping import *


def preprocess(text):
    nlp = get_nlp_pipeline()
    output = []
    text = replace_IOCs(text)
    paragraphs = split_by_new_lines(text)
    for paragraph in paragraphs:
        doc = nlp(paragraph)
        for sent in doc.sents:
            output.append(sent.text)
    return output


def extract(sentences):
    triplets = []
    for sentence in sentences:
        nlp = get_nlp_pipeline()
        sent = nlp(sentence)
        tokens = extract_tokens_from_sentence(sent)
        triplets.append(tokens)
    return triplets


def map_to_recovery(triplets, mapping_path):
    mappings = []
    for triplet in triplets:
        tripletList = list(triplet.values())
        mapping = map_to_recovery_from_triplets(tripletList, mapping_path)
        mappings.append(mapping)
    return mappings


def process(input_text, pipeline_stage):
    output_text = ""
    if pipeline_stage == "input":
        output_text = input_text
    elif pipeline_stage == "preprocess":
        output_text = "\n".join([str(item) for item in preprocess(input_text)])
    elif pipeline_stage == "extract":
        sentences = preprocess(input_text)
        output_text = "\n".join(
            [str(list(item.values())) for item in extract(sentences)]
        )
    elif pipeline_stage == "output":
        sentences = preprocess(input_text)
        triplets = extract(sentences)
        output_text = str(map_to_recovery(triplets))
    else:
        output_text = -1

    return output_text


def process_and_parse(input_text, mapping_path):
    sentences = preprocess(input_text)
    triplets = extract(sentences)
    mappings = map_to_recovery(triplets, mapping_path)

    return sentences, triplets, mappings
