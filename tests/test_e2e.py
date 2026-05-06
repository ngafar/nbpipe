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


def make_workflow(path, name, steps):
    """steps is a list of dicts with 'notebook' and optional 'output'."""
    lines = [f"name: {name}", "steps:"]
    for step in steps:
        lines.append(f"  - notebook: {step['notebook']}")
        if "output" in step:
            lines.append(f"    output: {step['output']}")
    path.write_text("\n".join(lines) + "\n")


def test_multi_step_pipeline(tmp_path):
    """Notebooks pass data to each other through files."""
    csv = tmp_path / "data.csv"
    result_txt = tmp_path / "result.txt"

    make_notebook(
        tmp_path / "extract.ipynb",
        [f"with open('{csv}', 'w') as f: f.write('a,b\\n1,2\\n3,4')"],
    )
    make_notebook(
        tmp_path / "transform.ipynb",
        [
            f"rows = open('{csv}').readlines()",
            "total = sum(int(r.split(',')[0]) for r in rows[1:])",
            f"open('{result_txt}', 'w').write(str(total))",
        ],
    )
    make_notebook(
        tmp_path / "verify.ipynb", [f"assert open('{result_txt}').read() == '4'"]
    )
    make_workflow(
        tmp_path / "wf.yaml",
        "pipeline",
        [
            {"notebook": "extract.ipynb", "output": str(csv)},
            {"notebook": "transform.ipynb", "output": str(result_txt)},
            {"notebook": "verify.ipynb"},
        ],
    )

    result = run_cli("run", str(tmp_path / "wf.yaml"))

    assert result.returncode == 0
    assert result_txt.read_text() == "4"


def test_fail_fast_on_error(tmp_path):
    """A failing notebook stops the pipeline; later notebooks do not run."""
    sentinel = tmp_path / "should_not_exist.txt"

    make_notebook(tmp_path / "ok.ipynb", ["x = 1"])
    make_notebook(tmp_path / "bad.ipynb", ["raise ValueError('step failed')"])
    make_notebook(tmp_path / "never.ipynb", [f"open('{sentinel}', 'w').write('ran')"])
    make_workflow(
        tmp_path / "wf.yaml",
        "failing",
        [
            {"notebook": "ok.ipynb"},
            {"notebook": "bad.ipynb"},
            {"notebook": "never.ipynb"},
        ],
    )

    result = run_cli("run", str(tmp_path / "wf.yaml"))

    assert result.returncode == 1
    assert not sentinel.exists()


def test_output_check_catches_missing_file(tmp_path):
    """A notebook that runs cleanly but skips writing its declared output fails the workflow."""
    make_notebook(tmp_path / "nb.ipynb", ["x = 1"])  # never writes the output
    make_workflow(
        tmp_path / "wf.yaml",
        "missing-output",
        [
            {"notebook": "nb.ipynb", "output": "report.csv"},
        ],
    )

    result = run_cli("run", str(tmp_path / "wf.yaml"))

    assert result.returncode == 1
    assert "report.csv" in result.stderr
