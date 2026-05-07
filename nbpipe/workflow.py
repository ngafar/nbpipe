from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class Step:
    notebook: Path
    output: Optional[Path] = None


@dataclass
class Workflow:
    name: str
    steps: list[Step]


def load_workflow(path: str | Path, base_dir: Path | None = None) -> Workflow:
    path = Path(path).resolve()
    base = Path(base_dir).resolve() if base_dir else path.parent

    with open(path) as f:
        data = yaml.safe_load(f)

    steps = [
        Step(
            notebook=base / item["notebook"],
            output=base / item["output"] if "output" in item else None,
        )
        for item in data["steps"]
    ]

    return Workflow(name=data["name"], steps=steps)
