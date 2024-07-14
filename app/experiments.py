import os
import json
import torch
import argparse

from tqdm import tqdm
from openai import OpenAI
from huggingface_hub.hf_api import HfFolder
from transformers import AutoTokenizer, pipeline

from pipeline.pipeline import process_and_parse


def semantic_model_experiment(input_folder, output_file, mapping_path):
    path = input_folder
    files = os.listdir(path)
    experiment_results = {}
    for file in tqdm(files):
        file_path = os.path.join(path, file)
        mapping_pairs = []
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            sentences, triplets, mappings = process_and_parse(content, mapping_path)
            for i in range(0, len(mappings)):
                for sugg in mappings[i]:
                    if sugg["action"]:
                        for obj in sugg["objects"]:
                            item = {}
                            item["sentence"] = sentences[i]
                            item["recovery_action"] = sugg["action"]
                            item["recovery_object"] = obj
                            mapping_pairs.append(item)

        experiment_results[file] = mapping_pairs
    with open(output_file, "w") as f:
        json.dump(experiment_results, f)


def get_gpt_answer(client, model, content):
    system_prompt = {
        "role": "system",
        "content": "You are an Incident Responder from a Security Operations Center. \n\nYour task is to "
        "execute the following instructions:\n1. analyze the given report;\n2. extract the "
        "recovery actions to be deployed under the described attack;\n3. identify the object "
        "on which the recovery action should be executed.\n4. If there is no recovery action "
        "for a certain sentence, discard it and don't include it in the output.\n\nOutput the "
        'answer in JSON using the following format: \n[\n  {\n    "sentence": sentence,'
        '\n    "recovery_action": recovery_action,\n    "object": object\n  }\n] ',
    }
    example_prompt = {
        "role": "user",
        "content": "The report of the attack is the following:\n\nThe malware adds a malicious "
        "executable. The executable encrypts \nthe user folder. This attack has high risk. ",
    }
    example_answer = {
        "role": "assistant",
        "content": '[\n  {\n    "sentence": "The malware adds a malicious executable.",'
        '\n    "recovery_action": "delete",\n    "object": "executable"\n  },'
        '\n  {\n    "sentence": "The executable encrypts the user folder.",'
        '\n    "recovery_action": "restore",\n    "object": "user folder"\n  }\n] ',
    }
    main_prompt = {
        "role": "user",
        "content": f"The report of the attack is the following:\n\n{content}",
    }
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[system_prompt, example_prompt, example_answer, main_prompt],
            temperature=0.25,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        answer = response.choices[0].message.content

    except Exception as e:
        print(e)
        answer = None

    return answer


def gpt_experiment(input_folder, output_folder, model):
    if not os.path.exists(output_folder):
        try:
            os.mkdir(output_folder)
        except:
            print(f"Something went wrong in creating {output_folder} folder.")
            return
    else:
        if os.path.isfile(output_folder):
            print("Please provide a folder for the output, instead of a file.")
            return

    api_key = input(
        "Please provide your OpenAI API key. Be aware, that running these experiments involves a cost!"
    )
    client = OpenAI(
        api_key=api_key,
    )

    path = input_folder
    files = os.listdir(path)
    for file in tqdm(files):
        file_path = os.path.join(path, file)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

            answer = get_gpt_answer(client, model, content)

            output_file = os.path.join(output_folder, f'{model}_{file}.txt')

            with open(output_file, "w") as f:
                f.write(answer)


def get_llama_response(prompt: str, llama_pipeline, tokenizer) -> None:
    sequences = llama_pipeline(
        prompt,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        max_length=4096,
    )
    return sequences


def llama_experiment(input_folder, output_folder):
    if not os.path.exists(output_folder):
        try:
            os.mkdir(output_folder)
        except:
            print(f"Something went wrong in creating {output_folder} folder.")
            return
    else:
        if os.path.isfile(output_folder):
            print("Please provide a folder for the output, instead of a file.")
            return

    api_key = input(
        "Please provide your HuggingFace API key."
    )
    HfFolder.save_token(api_key)
    # Initialize the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-13b-chat-hf")

    llama_pipeline = pipeline(
        "text-generation",  # LLM task
        model="meta-llama/Llama-2-13b-chat-hf",
        torch_dtype=torch.float16,
        device_map="auto",
    )

    files = os.listdir(input_folder)
    for filename in files:
        path = os.path.join(input_folder, filename)
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()

                prompt = f"""<s>[INST] <<SYS>>
You are an Incident Responder from a Security Operations Center. Your task is to execute the following instructions:
1. analyze the given report; 
2. extract the recovery actions to be deployed under the described attack; 
3. identify the object on which the recovery action should be executed.
If there is no recovery action for a certain sentence, discard it and don't include it in the output.

Output the answer in JSON using the following format: {{"sentence": sentence, "recovery_action": recovery_action, "object": object}}

<</SYS>>

The report of the attack is the following:

The malware adds a malicious executable. The executable encrypts the user folder. This attack has high risk. [/INST]
[
{{"sentence": "The malware adds a malicious executable.", "recovery_action": "delete", "object": "executable"}},
{{"sentence": "The executable encrypts the user folder.", "recovery_action": "restore", "object": "user folder"}},
] </s>

<s>[INST]  
The report of the attack is the following:

{content}
[/INST]"""
                responses = get_llama_response(prompt, llama_pipeline, tokenizer)
                for response in responses:
                    path = os.path.join(output_folder, f"llama2_{filename}.txt")
                    with open(path, "w", encoding="utf-8") as outfile:
                        outfile.write(response["generated_text"][len(prompt) :])
        except Exception as e:
            path = os.path.join(output_folder, f"error_{filename}.txt")
            with open(path, "w", encoding="utf-8") as outfile:
                outfile.write(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Path to the input dataset folder.", required=True)
    parser.add_argument("-o", "--output", help="Path to the output. The semantic model outputs a JSON file, while the generative models write the output into a folder.", required=True)
    parser.add_argument("-m", "--model", help="Name of the model to use for the experiment.", choices=['semantic', 'llama', 'gpt-3.5-turbo-1106', 'gpt-4', 'gpt-4-turbo-preview'], required=True)
    args = parser.parse_args()

    model = args.model

    if model == 'semantic':
        semantic_model_experiment(args.input, args.output, 'mapping_OpenC2.json')
    elif model == 'llama':
        llama_experiment(args.input, args.output)
    else:
        gpt_experiment(args.input, args.output, model=model)
