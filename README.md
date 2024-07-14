# Recovery Inference

This repository contains the code of the DIMVA paper Inferring Recovery Steps from Cyber Threat Intelligence Reports [1]. To read the paper, click on the following [link](https://research.utwente.nl/files/422055625/kucsvan-recovery-2024.pdf).

## Directory Structure
```
.
├── app: contains the code for running the tool
├── data: contains the labeled dataset used for the experiments
└── results: contains the results of the experiments
```

## Documentation

1. Clone this repository
```bash
git clone https://github.com/utwente-scs/recovery-inference.git
```

### How to run the experiments

For running the experiments, first change to the `app` directory.

```bash
$ cd app
```

Then follow these steps:

1. Make sure you have `virtualenv` installed

```bash
$ pip install virtualenv
```

2. Create a virtual environment

```bash
$ virtualenv venv 
```

3. Activate the virtual environment

```bash 
$ source venv/bin/activate
```

3. Install the requirements.txt

```bash
$ pip install -r requirements.txt
```

4. Run the experiments

```bash 
$ python experiments.py -i INPUT_PATH -o OUTPUT_PATH -m {semantic,llama,gpt-3.5-turbo-1106,gpt-4,gpt-4-turbo-preview}
```

### How to run the tool in GUI mode

1. Make sure docker is installed and running. (For more details, please check the official [documentation](https://docs.docker.com/engine/install/).)

2. Build and run the container.

```bash
$ docker compose up --build
```

3. Access the GUI in a web browser: `http://127.0.0.1:5000`.

## References
[1] `Kucsván, Z. L., Caselli, M., Peter, A., & Continella, A. (2024, July). Inferring Recovery Steps from Cyber Threat Intelligence Reports. In Proceedings of the Conference on Detection of Intrusions and Malware and Vulnerability Assessment (DIMVA), 2024.`

### Bibtex
```
@inproceedings{kucsvan2024inferring,
 title = {Inferring Recovery Steps from Cyber Threat Intelligence Reports},
 author={Kucsván, Zsolt Levente and Caselli, Marco and Peter, Andreas and Continella, Andrea},
 booktitle = {In Proceedings of the Conference on Detection of Intrusions and Malware and Vulnerability Assessment (DIMVA)},
 year = {2024}
}
```