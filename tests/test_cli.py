import subprocess
from pathlib import Path

import nbformat

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
    lines = [f"name: {name}", "steps:"]
    for nb in notebooks:
        lines.append(f"  - notebook: {nb}")
    path.write_text("\n".join(lines) + "\n")


def nbpipe_dir(tmp_path):
    d = tmp_path / ".nbpipe"
    d.mkdir()
    return d


def test_run_workflow_succeeds(tmp_path):
    make_notebook(tmp_path / "nb.ipynb", ["print('ok')"])
    make_workflow(nbpipe_dir(tmp_path) / "wf.yaml", "test", ["nb.ipynb"])

    result = run_cli("run", str(tmp_path / ".nbpipe/wf.yaml"))

    assert result.returncode == 0
    assert "done" in result.stdout


def test_run_workflow_output_contains_name(tmp_path):
    make_notebook(tmp_path / "nb.ipynb", ["x = 1"])
    make_workflow(nbpipe_dir(tmp_path) / "wf.yaml", "my_pipeline", ["nb.ipynb"])

    result = run_cli("run", str(tmp_path / ".nbpipe/wf.yaml"))

    assert "my_pipeline" in result.stdout


def test_run_missing_workflow_file(tmp_path):
    result = run_cli("run", str(tmp_path / ".nbpipe/missing.yaml"))

    assert result.returncode == 1


def test_run_failing_notebook_exits_nonzero(tmp_path):
    make_notebook(tmp_path / "bad.ipynb", ["raise RuntimeError('boom')"])
    make_workflow(nbpipe_dir(tmp_path) / "wf.yaml", "test", ["bad.ipynb"])

    result = run_cli("run", str(tmp_path / ".nbpipe/wf.yaml"))

    assert result.returncode == 1
    assert "FAILED" in result.stdout or "FAILED" in result.stderr


def test_no_command_exits_nonzero():
    result = run_cli()

    assert result.returncode == 1


def test_run_multiple_notebooks_in_order(tmp_path):
    out = tmp_path / "out.txt"
    make_notebook(tmp_path / "a.ipynb", [f"open('{out}', 'w').write('hello')"])
    make_notebook(tmp_path / "b.ipynb", [f"print(open('{out}').read())"])
    make_workflow(nbpipe_dir(tmp_path) / "wf.yaml", "chained", ["a.ipynb", "b.ipynb"])

    result = run_cli("run", str(tmp_path / ".nbpipe/wf.yaml"))

    assert result.returncode == 0


def test_output_check_passes_when_file_exists(tmp_path):
    out_file = tmp_path / "result.csv"
    make_notebook(tmp_path / "nb.ipynb", [f"open('{out_file}', 'w').write('data')"])
    wf = "name: test\nsteps:\n  - notebook: nb.ipynb\n    output: result.csv\n"
    nbpipe_dir(tmp_path).joinpath("wf.yaml").write_text(wf)

    result = run_cli("run", str(tmp_path / ".nbpipe/wf.yaml"))

    assert result.returncode == 0


def test_run_workflow_yml_extension(tmp_path):
    make_notebook(tmp_path / "nb.ipynb", ["x = 1"])
    wf = "name: test\nsteps:\n  - notebook: nb.ipynb\n"
    nbpipe_dir(tmp_path).joinpath("wf.yml").write_text(wf)

    result = run_cli("run", str(tmp_path / ".nbpipe/wf.yml"))

    assert result.returncode == 0


def test_output_check_fails_when_file_missing(tmp_path):
    make_notebook(tmp_path / "nb.ipynb", ["x = 1"])
    wf = "name: test\nsteps:\n  - notebook: nb.ipynb\n    output: missing.csv\n"
    nbpipe_dir(tmp_path).joinpath("wf.yaml").write_text(wf)

    result = run_cli("run", str(tmp_path / ".nbpipe/wf.yaml"))

    assert result.returncode == 1
    assert "missing.csv" in result.stderr


def test_output_wildcard_passes_when_matching_file_exists(tmp_path):
    out_file = tmp_path / "report_2024-01-15.csv"
    make_notebook(tmp_path / "nb.ipynb", [f"open('{out_file}', 'w').write('data')"])
    wf = "name: test\nsteps:\n  - notebook: nb.ipynb\n    output: report_*.csv\n"
    nbpipe_dir(tmp_path).joinpath("wf.yaml").write_text(wf)

    result = run_cli("run", str(tmp_path / ".nbpipe/wf.yaml"))

    assert result.returncode == 0


def test_output_wildcard_fails_when_no_matching_file(tmp_path):
    make_notebook(tmp_path / "nb.ipynb", ["x = 1"])
    wf = "name: test\nsteps:\n  - notebook: nb.ipynb\n    output: report_*.csv\n"
    nbpipe_dir(tmp_path).joinpath("wf.yaml").write_text(wf)

    result = run_cli("run", str(tmp_path / ".nbpipe/wf.yaml"))

    assert result.returncode == 1
    assert "report_" in result.stderr



def test_yaml_timeout_exits_nonzero_with_message(tmp_path):
    make_notebook(tmp_path / "nb.ipynb", ["import time; time.sleep(30)"])
    wf = "name: test\nsteps:\n  - notebook: nb.ipynb\n    timeout: 1\n"
    nbpipe_dir(tmp_path).joinpath("wf.yaml").write_text(wf)

    result = run_cli("run", str(tmp_path / ".nbpipe/wf.yaml"))

    assert result.returncode == 1
    assert "timed out" in result.stderr
