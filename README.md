# nbpipe

Run sequences of Jupyter notebooks as a workflow from the command line.

## Installation

```bash
pip install nbpipe
```

## Usage

Define a workflow in a YAML file:

```yaml
name: my_workflow
steps:
  - notebook: prepare_data.ipynb
    output: data/processed.csv
  - notebook: train_model.ipynb
    output: models/model.pkl
  - notebook: evaluate.ipynb
```

Then run it:

```bash
nbpipe run workflow.yaml
```

Each notebook is executed in place — cell outputs are written back to the `.ipynb` file, and any files the notebook saves to disk are its real outputs.

If a step has an `output` field, nbpipe checks that the file exists after the notebook runs and raises an error if it does not. Steps without an `output` field are always considered successful as long as no cell raises an exception.

## Workflow YAML

| Field | Required | Description |
|-------|----------|-------------|
| `name` | yes | Name of the workflow |
| `steps` | yes | Ordered list of steps to run |

Each step:

| Field | Required | Description |
|-------|----------|-------------|
| `notebook` | yes | Path to the `.ipynb` file (relative to the YAML file) |
| `output` | no | Path to a file the notebook is expected to produce |

All paths are relative to the directory containing the YAML file.
