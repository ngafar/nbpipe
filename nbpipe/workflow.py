from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class NotebookStep:
    path: Path


@dataclass
class Workflow:
    name: str
    notebooks: list[NotebookStep]


def load_workflow(path: str | Path) -> Workflow:
    path = Path(path).resolve()
    base = path.parent

    with open(path) as f:
        data = yaml.safe_load(f)

    notebooks = [NotebookStep(path=base / item) for item in data["notebooks"]]

    return Workflow(name=data["name"], notebooks=notebooks)
