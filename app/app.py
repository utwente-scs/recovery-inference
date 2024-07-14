from flask import Flask, render_template, request, jsonify
from pipeline import pipeline
from utils.utils import *

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["TEMPLATES_AUTO_RELOAD"] = True  # Enable template auto-reloading
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # Disable caching for static files


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process_text():
    data = request.get_json()
    input_text = data.get("text")
    pipeline_stage = data.get("pipelineStage")
    if input_text:
        mapping_path = 'mapping_OpenC2.json'
        sentences, triplets, mappings = pipeline.process_and_parse(input_text, mapping_path)

        output = parse_data_to_json(input_text, sentences, triplets, mappings)

        if output == -1:
            output = f"There is no pipeline with the name: {pipeline_stage}"

        return jsonify(output)
    else:
        return jsonify({"output": "Invalid input"})


if __name__ == "__main__":
    app.run()
