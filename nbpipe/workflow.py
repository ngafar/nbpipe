import glob as _glob
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class Step:
    notebook: Path
    output: Optional[Path] = None
    output_pattern: Optional[str] = None


@dataclass
class Workflow:
    name: str
    steps: list[Step]


def _glob_one(base: Path, pattern: str) -> Path:
    matches = sorted(
        Path(p) for p in _glob.glob(str(Path(_glob.escape(str(base))) / pattern))
    )
    if not matches:
        raise FileNotFoundError(f"No notebook matched pattern '{pattern}'")
    if len(matches) > 1:
        raise ValueError(
            f"Notebook pattern '{pattern}' matched multiple files: "
            + ", ".join(str(m) for m in matches)
        )
    return matches[0]


def load_workflow(path: str | Path, base_dir: Path | None = None) -> Workflow:
    path = Path(path).resolve()
    base = Path(base_dir).resolve() if base_dir else path.parent

    with open(path) as f:
        data = yaml.safe_load(f)

    steps = []
    for item in data["steps"]:
        nb = item["notebook"]
        notebook = _glob_one(base, nb) if "*" in nb else base / nb

        output = None
        output_pattern = None
        if "output" in item:
            out = item["output"]
            if "*" in out:
                output_pattern = str(Path(_glob.escape(str(base))) / out)
            else:
                output = base / out

        steps.append(
            Step(notebook=notebook, output=output, output_pattern=output_pattern)
        )

    return Workflow(name=data["name"], steps=steps)
