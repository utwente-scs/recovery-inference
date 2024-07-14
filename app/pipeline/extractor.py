import spacy
from spacy.symbols import dobj, nsubj, nsubjpass, neg, conj, appos

nlp = None
SPACY_MODEL = "en_core_web_trf"


def get_nlp_pipeline():
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load(SPACY_MODEL)
        except:
            try:
                spacy.cli.download(SPACY_MODEL)
                nlp = spacy.load(SPACY_MODEL)
            except:
                print(f"ERROR localizing model: {SPACY_MODEL}")
    return nlp


def search_root_verb_token(token):
    if token.tag_.startswith("VB"):
        return token
    if token.dep_ == "ROOT":
        return None
    return search_root_verb_token(token.head)


def search_verb_root(item):
    if item.dep in [conj]:
        return search_verb_root(item.head)
    return item


def add_verb_tokens(item, tokens):
    if item is None:
        return
    if item.tag_.startswith("VB"):
        if item in tokens:
            return
        root_verb = search_verb_root(item)
        if root_verb.dep_ == "ROOT":
            tokens[item] = {"subjects": [], "action": item, "negated": False, "objects": []}


def search_noun_root(item):
    if item.dep in [conj, appos]:
        return search_noun_root(item.head)
    return item


def add_noun_tokens(item, dependencies, category, tokens):
    root = search_noun_root(item.root)
    if '_' in item.text:
        return
    root_verb = root.head
    if root.dep in dependencies and root_verb in tokens:
        tokens[root_verb][category].append(item.root)


def predict_subjects(tokens):
    main_subjs = []
    for token in tokens:
        if token.dep_ == "ROOT":
            main_subjs = tokens[token]["subjects"]
            break
    for token in tokens:
        if len(tokens[token]["subjects"]) == 0:
            tokens[token]["subjects"] = main_subjs


def extract_tokens_from_sentence(sentence):
    tokens = {}
    for token in sentence:
        add_verb_tokens(token, tokens)
    for token in sentence:
        if token.dep == neg and token.head in tokens:
            tokens[token.head]["negated"] = True
    for noun in sentence.noun_chunks:
        add_noun_tokens(noun, [dobj], "objects", tokens)
        add_noun_tokens(noun, [nsubj, nsubjpass], "subjects", tokens)

    predict_subjects(tokens)
    return tokens
