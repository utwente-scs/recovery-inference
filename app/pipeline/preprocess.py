import json
from iocsearcher.searcher import Searcher


def concatenate_sentences(sentences):
    if len(sentences) == 0:
        return 0, []
    sentence = sentences[0].strip()
    if sentence == "" or sentence[-1] not in ".?!":
        count, concatenated = concatenate_sentences(sentences[1:])
        if sentence != "":
            concatenated.append(sentence)
        return count + 1, concatenated
    else:
        if sentence != "" and sentence[-1] in ".?!":
            return 0, []
        return 0, [sentence]


def split_by_new_lines(input_text):
    paragraphs = input_text.split("\n")
    result = []
    length = len(paragraphs)
    index = 0
    while index < length:
        paragraph = paragraphs[index].strip()
        if paragraph == "":
            index += 1
            continue
        if paragraph[-1] == ":":
            first_sentence = paragraph
            step, paragraph = concatenate_sentences(paragraphs[index + 1:])
            index = index + step
            paragraph.reverse()
            paragraph = ", ".join(paragraph)
            paragraph = first_sentence + " " + paragraph.strip()
        if paragraph[-1] not in ".?!":
            paragraph += "."
        index += 1
        result.append(paragraph)
    return result


replacements = {}
replacement_dictionary = {}


def replace_IOCs(input_text):
    regex = r"\s((?P<ParentPath>(?:(?P<Win_dir>[\w\-]\:)|(?P<samba>(?:\/|\\)(?:\/|\\)[\w \.\d]+(?:\/|\\)[\w \.$]+)|(?P<ENV>%[\w\d ]+%)|(?P<cur_dir>\.)|(?P<par_dir>\.\.)|(?P<folder>[\w\-]+))(?:(?:\/|\\))(?P<inner>[\w\-{} \.]+(?:\/|\\))*)(?P<BaseName>(?P<file>[\w\- ]+\.[\w]{2,4})|(?P<directory>[\w\-]+)|(?P<folder_>{[\w\- \.]+})|(?P<none>)))"
    regex2 = r"\%[a-zA-Z _]+?\%"
    regex3 = r"(https?://([\w\d{}]+.)+[\w\d]+(/[\w\d.?=&-]+)*)"
    regex4 = r"\([Nn]ote.*?\.\)"

    searcher = Searcher()

    searcher.add_regexp('path', regex, validate=False)
    searcher.add_regexp('env', regex2, validate=False)
    searcher.add_regexp('myurl', regex3, validate=False)
    searcher.add_regexp('explanation', regex4, validate=False)

    ioc_results = searcher.search_raw(input_text)
    ioc_results.sort(key=lambda a: a[2])

    return_text = ""
    orig_end = 0

    for result in ioc_results:
        ioctype = result[0]
        start = result[2]
        end = start + len(result[1])
        if ioctype not in replacements:
            replacements[ioctype] = 0
        else:
            replacements[ioctype] += 1
        return_text += input_text[orig_end:start]
        return_text += f"{ioctype}_{replacements[ioctype]}"
        replacement_dictionary[f"{ioctype}_{replacements[ioctype]}"] = result[1]
        orig_end = end
    return_text += input_text[orig_end:]

    with open("replacements.json", "w") as outfile:
        json.dump(replacement_dictionary, outfile)

    return return_text

