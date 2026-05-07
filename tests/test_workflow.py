import pytest
from nbpipe.workflow import load_workflow


def write_yaml(path, content):
    path.write_text(content)
    return path


def test_load_simple(tmp_path):
    f = write_yaml(
        tmp_path / "wf.yaml",
        "name: my_workflow\nsteps:\n  - notebook: a.ipynb\n  - notebook: b.ipynb\n",
    )
    wf = load_workflow(f)

    assert wf.name == "my_workflow"
    assert len(wf.steps) == 2
    assert wf.steps[0].notebook == tmp_path / "a.ipynb"
    assert wf.steps[1].notebook == tmp_path / "b.ipynb"


def test_paths_resolve_relative_to_yaml(tmp_path):
    sub = tmp_path / "subdir"
    sub.mkdir()
    f = write_yaml(sub / "wf.yaml", "name: test\nsteps:\n  - notebook: step.ipynb\n")

    wf = load_workflow(f)

    assert wf.steps[0].notebook == sub / "step.ipynb"


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_workflow(tmp_path / "missing.yaml")


def test_output_field_parsed(tmp_path):
    f = write_yaml(
        tmp_path / "wf.yaml",
        "name: x\nsteps:\n  - notebook: n.ipynb\n    output: results/out.csv\n",
    )
    wf = load_workflow(f)

    assert wf.steps[0].output == tmp_path / "results/out.csv"


def test_output_field_optional(tmp_path):
    f = write_yaml(tmp_path / "wf.yaml", "name: x\nsteps:\n  - notebook: n.ipynb\n")
    wf = load_workflow(f)

    assert wf.steps[0].output is None


def test_output_resolves_relative_to_yaml(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    f = write_yaml(
        sub / "wf.yaml",
        "name: x\nsteps:\n  - notebook: n.ipynb\n    output: out/file.csv\n",
    )
    wf = load_workflow(f)

    assert wf.steps[0].output == sub / "out/file.csv"
