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


def test_base_dir_overrides_yaml_directory(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    f = write_yaml(sub / "wf.yaml", "name: x\nsteps:\n  - notebook: n.ipynb\n")
    wf = load_workflow(f, base_dir=tmp_path)

    assert wf.steps[0].notebook == tmp_path / "n.ipynb"


def test_output_resolves_relative_to_yaml(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    f = write_yaml(
        sub / "wf.yaml",
        "name: x\nsteps:\n  - notebook: n.ipynb\n    output: out/file.csv\n",
    )
    wf = load_workflow(f)

    assert wf.steps[0].output == sub / "out/file.csv"


def test_notebook_wildcard_resolves_single_match(tmp_path):
    (tmp_path / "report_2024-01-15.ipynb").write_text("{}")
    f = write_yaml(
        tmp_path / "wf.yaml",
        "name: x\nsteps:\n  - notebook: report_*.ipynb\n",
    )
    wf = load_workflow(f)

    assert wf.steps[0].notebook == tmp_path / "report_2024-01-15.ipynb"


def test_notebook_wildcard_no_match_raises(tmp_path):
    f = write_yaml(
        tmp_path / "wf.yaml", "name: x\nsteps:\n  - notebook: report_*.ipynb\n"
    )

    with pytest.raises(FileNotFoundError, match="report_\\*.ipynb"):
        load_workflow(f)


def test_notebook_wildcard_multiple_matches_raises(tmp_path):
    (tmp_path / "report_a.ipynb").write_text("{}")
    (tmp_path / "report_b.ipynb").write_text("{}")
    f = write_yaml(
        tmp_path / "wf.yaml", "name: x\nsteps:\n  - notebook: report_*.ipynb\n"
    )

    with pytest.raises(ValueError, match="multiple"):
        load_workflow(f)


def test_output_wildcard_stores_pattern(tmp_path):
    f = write_yaml(
        tmp_path / "wf.yaml",
        "name: x\nsteps:\n  - notebook: n.ipynb\n    output: results_*.csv\n",
    )
    wf = load_workflow(f)

    assert wf.steps[0].output is None
    assert wf.steps[0].output_pattern == str(tmp_path / "results_*.csv")


def test_output_literal_sets_no_pattern(tmp_path):
    f = write_yaml(
        tmp_path / "wf.yaml",
        "name: x\nsteps:\n  - notebook: n.ipynb\n    output: results.csv\n",
    )
    wf = load_workflow(f)

    assert wf.steps[0].output == tmp_path / "results.csv"
    assert wf.steps[0].output_pattern is None


def test_notebook_wildcard_base_with_glob_special_chars(tmp_path):
    base = tmp_path / "project[v1]"
    base.mkdir()
    (base / "report_jan.ipynb").write_text("{}")
    f = write_yaml(base / "wf.yaml", "name: x\nsteps:\n  - notebook: report_*.ipynb\n")

    wf = load_workflow(f)

    assert wf.steps[0].notebook == base / "report_jan.ipynb"


def test_output_wildcard_base_with_glob_special_chars(tmp_path):
    import glob as _glob

    base = tmp_path / "project[v1]"
    base.mkdir()
    (base / "results_jan.csv").write_text("data")
    f = write_yaml(
        base / "wf.yaml",
        "name: x\nsteps:\n  - notebook: n.ipynb\n    output: results_*.csv\n",
    )

    wf = load_workflow(f)

    assert _glob.glob(wf.steps[0].output_pattern) == [str(base / "results_jan.csv")]
