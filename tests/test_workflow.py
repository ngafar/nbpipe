import pytest
from nbpipe.workflow import NotebookStep, Workflow, load_workflow


def write_yaml(path, content):
    path.write_text(content)
    return path


def test_load_simple(tmp_path):
    f = write_yaml(tmp_path / "wf.yaml", "name: my_workflow\nnotebooks:\n  - a.ipynb\n  - b.ipynb\n")
    wf = load_workflow(f)

    assert wf.name == "my_workflow"
    assert len(wf.notebooks) == 2
    assert wf.notebooks[0].path == tmp_path / "a.ipynb"
    assert wf.notebooks[1].path == tmp_path / "b.ipynb"


def test_paths_resolve_relative_to_yaml(tmp_path):
    sub = tmp_path / "subdir"
    sub.mkdir()
    f = write_yaml(sub / "wf.yaml", "name: test\nnotebooks:\n  - step.ipynb\n")

    wf = load_workflow(f)

    assert wf.notebooks[0].path == sub / "step.ipynb"


def test_returns_workflow_dataclass(tmp_path):
    f = write_yaml(tmp_path / "wf.yaml", "name: x\nnotebooks:\n  - n.ipynb\n")
    wf = load_workflow(f)

    assert isinstance(wf, Workflow)
    assert isinstance(wf.notebooks[0], NotebookStep)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_workflow(tmp_path / "missing.yaml")


def test_single_notebook(tmp_path):
    f = write_yaml(tmp_path / "wf.yaml", "name: solo\nnotebooks:\n  - only.ipynb\n")
    wf = load_workflow(f)

    assert len(wf.notebooks) == 1
