# nbpipe

Run sequences of Jupyter notebooks as a workflow from the command line or the JupyterLab sidebar.

![nbpipe demo](https://raw.githubusercontent.com/ngafar/nbpipe/main/assets/nbpipe-demo.gif)

## Installation

```bash
pip install nbpipe
```

## Usage

Create a `.nbpipe/` directory at the root of your project and add a workflow YAML file inside it. 

```yaml
# .nbpipe/my_workflow.yaml

name: my_workflow
steps:
  - notebook: prepare_data.ipynb
    output: data/processed.csv
  - notebook: train_model.ipynb
```

Run it from the CLI:

```bash
nbpipe run .nbpipe/my_workflow.yaml
```

or from the JupyterLab sidebar.

## Step fields

| Field | Required | Description |
|-------|----------|-------------|
| `notebook` | yes | Notebook to run, relative to the project root |
| `output` | no | File the notebook must produce — workflow fails if absent. Supports wildcards (e.g. `report_*.csv`) for files with dynamic names such as timestamps |
