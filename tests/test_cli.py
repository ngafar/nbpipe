import subprocess
import sys
from pathlib import Path

import nbformat
import pytest

PROJECT_ROOT = Path(__file__).parent.parent


def run_cli(*args):
    return subprocess.run(
        ["uv", "run", "nbpipe", *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


def make_notebook(path, sources):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(src) for src in sources]
    nbformat.write(nb, str(path))


def make_workflow(path, name, notebooks):
    lines = [f"name: {name}", "notebooks:"]
    for nb in notebooks:
        lines.append(f"  - {nb}")
    path.write_text("\n".join(lines) + "\n")


def test_run_workflow_succeeds(tmp_path):
    make_notebook(tmp_path / "nb.ipynb", ["print('ok')"])
    make_workflow(tmp_path / "wf.yaml", "test", ["nb.ipynb"])

    result = run_cli("run", str(tmp_path / "wf.yaml"))

    assert result.returncode == 0
    assert "done" in result.stdout


def test_run_workflow_output_contains_name(tmp_path):
    make_notebook(tmp_path / "nb.ipynb", ["x = 1"])
    make_workflow(tmp_path / "wf.yaml", "my_pipeline", ["nb.ipynb"])

    result = run_cli("run", str(tmp_path / "wf.yaml"))

    assert "my_pipeline" in result.stdout


def test_run_missing_workflow_file(tmp_path):
    result = run_cli("run", str(tmp_path / "missing.yaml"))

    assert result.returncode == 1


def test_run_failing_notebook_exits_nonzero(tmp_path):
    make_notebook(tmp_path / "bad.ipynb", ["raise RuntimeError('boom')"])
    make_workflow(tmp_path / "wf.yaml", "test", ["bad.ipynb"])

    result = run_cli("run", str(tmp_path / "wf.yaml"))

    assert result.returncode == 1
    assert "FAILED" in result.stdout or "FAILED" in result.stderr


def test_no_command_exits_nonzero():
    result = run_cli()

    assert result.returncode == 1


def test_run_multiple_notebooks_in_order(tmp_path):
    # second notebook depends on a file written by the first
    make_notebook(tmp_path / "a.ipynb", ["open('out.txt', 'w').write('hello')"])
    make_notebook(tmp_path / "b.ipynb", ["print(open('out.txt').read())"])
    make_workflow(tmp_path / "wf.yaml", "chained", ["a.ipynb", "b.ipynb"])

    result = run_cli("run", str(tmp_path / "wf.yaml"))

    assert result.returncode == 0
