import json

import nbformat


def make_notebook(path, sources):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(src) for src in sources]
    nbformat.write(nb, str(path))


def make_workflow(path, name, steps):
    lines = [f"name: {name}", "steps:"]
    for step in steps:
        lines.append(f"  - notebook: {step['notebook']}")
        if "output" in step:
            lines.append(f"    output: {step['output']}")
    path.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# GET /nbpipe/workflows
# ---------------------------------------------------------------------------


async def test_get_workflows_no_nbpipe_dir(jp_fetch, jp_root_dir):
    response = await jp_fetch("nbpipe", "workflows")
    assert response.code == 200
    assert json.loads(response.body) == []


async def test_get_workflows_empty_dir(jp_fetch, jp_root_dir):
    (jp_root_dir / ".nbpipe").mkdir()
    response = await jp_fetch("nbpipe", "workflows")
    assert response.code == 200
    assert json.loads(response.body) == []


async def test_get_workflows_yaml(jp_fetch, jp_root_dir):
    nbpipe_dir = jp_root_dir / ".nbpipe"
    nbpipe_dir.mkdir()
    make_workflow(nbpipe_dir / "pipeline.yaml", "pipeline", [{"notebook": "nb.ipynb"}])

    response = await jp_fetch("nbpipe", "workflows")
    assert json.loads(response.body) == [{"name": "pipeline"}]


async def test_get_workflows_yml(jp_fetch, jp_root_dir):
    nbpipe_dir = jp_root_dir / ".nbpipe"
    nbpipe_dir.mkdir(exist_ok=True)
    make_workflow(nbpipe_dir / "pipeline.yml", "pipeline", [{"notebook": "nb.ipynb"}])

    response = await jp_fetch("nbpipe", "workflows")
    assert json.loads(response.body) == [{"name": "pipeline"}]


async def test_get_workflows_sorted(jp_fetch, jp_root_dir):
    nbpipe_dir = jp_root_dir / ".nbpipe"
    nbpipe_dir.mkdir(exist_ok=True)
    for name in ["beta.yaml", "alpha.yaml", "gamma.yml"]:
        make_workflow(nbpipe_dir / name, name, [{"notebook": "nb.ipynb"}])

    response = await jp_fetch("nbpipe", "workflows")
    names = [w["name"] for w in json.loads(response.body)]
    assert names == sorted(names)


# ---------------------------------------------------------------------------
# POST /nbpipe/workflows/{name}/run
# ---------------------------------------------------------------------------


async def test_run_workflow_not_found(jp_fetch):
    response = await jp_fetch(
        "nbpipe",
        "workflows",
        "missing",
        "run",
        method="POST",
        body="",
        raise_error=False,
    )
    assert response.code == 404


async def test_run_workflow_success(jp_fetch, jp_root_dir):
    nbpipe_dir = jp_root_dir / ".nbpipe"
    nbpipe_dir.mkdir()
    make_notebook(jp_root_dir / "nb.ipynb", ["x = 1 + 1"])
    make_workflow(nbpipe_dir / "simple.yaml", "simple", [{"notebook": "nb.ipynb"}])

    response = await jp_fetch(
        "nbpipe",
        "workflows",
        "simple",
        "run",
        method="POST",
        body="",
    )
    assert response.code == 200
    assert json.loads(response.body) == {"status": "ok"}


async def test_run_workflow_yml_extension(jp_fetch, jp_root_dir):
    nbpipe_dir = jp_root_dir / ".nbpipe"
    nbpipe_dir.mkdir()
    make_notebook(jp_root_dir / "nb.ipynb", ["x = 1"])
    make_workflow(nbpipe_dir / "simple.yml", "simple", [{"notebook": "nb.ipynb"}])

    response = await jp_fetch(
        "nbpipe",
        "workflows",
        "simple",
        "run",
        method="POST",
        body="",
    )
    assert response.code == 200


async def test_run_workflow_cell_error_returns_500(jp_fetch, jp_root_dir):
    nbpipe_dir = jp_root_dir / ".nbpipe"
    nbpipe_dir.mkdir()
    make_notebook(jp_root_dir / "nb.ipynb", ["raise ValueError('boom')"])
    make_workflow(nbpipe_dir / "bad.yaml", "bad", [{"notebook": "nb.ipynb"}])

    response = await jp_fetch(
        "nbpipe",
        "workflows",
        "bad",
        "run",
        method="POST",
        body="",
        raise_error=False,
    )
    assert response.code == 500


async def test_run_workflow_missing_output_returns_500(jp_fetch, jp_root_dir):
    nbpipe_dir = jp_root_dir / ".nbpipe"
    nbpipe_dir.mkdir()
    make_notebook(jp_root_dir / "nb.ipynb", ["x = 1"])
    make_workflow(
        nbpipe_dir / "checked.yaml",
        "checked",
        [{"notebook": "nb.ipynb", "output": "missing.csv"}],
    )

    response = await jp_fetch(
        "nbpipe",
        "workflows",
        "checked",
        "run",
        method="POST",
        body="",
        raise_error=False,
    )
    assert response.code == 500
