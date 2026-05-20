import asyncio
import glob as _glob
import json
from pathlib import Path

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

from .runner import execute_notebook
from .workflow import load_workflow


class WorkflowsHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        nbpipe_dir = Path(self.settings["server_root_dir"]).expanduser() / ".nbpipe"
        workflows = []
        if nbpipe_dir.exists():
            by_stem: dict[str, Path] = {}
            for f in sorted([*nbpipe_dir.glob("*.yaml"), *nbpipe_dir.glob("*.yml")]):
                by_stem.setdefault(f.stem, f)  # .yaml wins over .yml (sorts first)
            workflows = [{"name": stem} for stem in sorted(by_stem)]
        self.finish(json.dumps(workflows))


class RunWorkflowHandler(APIHandler):
    @tornado.web.authenticated
    async def post(self, name):
        root = Path(self.settings["server_root_dir"]).expanduser()
        yaml_path = root / ".nbpipe" / f"{name}.yaml"
        if not yaml_path.exists():
            yaml_path = root / ".nbpipe" / f"{name}.yml"
        if not yaml_path.exists():
            raise tornado.web.HTTPError(404, f"Workflow '{name}' not found")

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _run_workflow, yaml_path, root)
        except Exception as exc:
            raise tornado.web.HTTPError(500, str(exc))

        self.finish(json.dumps({"status": "ok"}))


def _run_workflow(yaml_path: Path, base_dir: Path) -> None:
    workflow = load_workflow(yaml_path, base_dir=base_dir)
    for step in workflow.steps:
        execute_notebook(step.notebook)
        if step.output_pattern:
            if not _glob.glob(step.output_pattern):
                raise RuntimeError(f"No output matched pattern: {step.output_pattern}")
        elif step.output and not step.output.exists():
            raise RuntimeError(f"Expected output not found: {step.output}")


def setup_handlers(web_app) -> None:
    base = web_app.settings["base_url"]
    web_app.add_handlers(
        ".*$",
        [
            (url_path_join(base, "nbpipe", "workflows"), WorkflowsHandler),
            (
                url_path_join(base, "nbpipe", "workflows", r"([^/]+)", "run"),
                RunWorkflowHandler,
            ),
        ],
    )
