import asyncio
import glob as _glob
import json
from pathlib import Path

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

from .runner import StopToken, WorkflowStoppedError, execute_notebook
from .workflow import load_workflow

_stop_tokens: dict[str, StopToken] = {}


class WorkflowsHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        nbpipe_dir = Path(self.settings["server_root_dir"]).expanduser() / ".nbpipe"
        workflows = []
        if nbpipe_dir.exists():
            by_stem: dict[str, Path] = {}
            for f in sorted([*nbpipe_dir.glob("*.yaml"), *nbpipe_dir.glob("*.yml")]):
                by_stem.setdefault(f.stem, f)  # .yaml wins over .yml (sorts first)
            workflows = [
                {"name": stem, "path": f".nbpipe/{stem}{by_stem[stem].suffix}"}
                for stem in sorted(by_stem)
            ]
        self.finish(json.dumps(workflows))


class RunWorkflowHandler(APIHandler):
    @tornado.web.authenticated
    async def post(self, name):
        if name in _stop_tokens:
            raise tornado.web.HTTPError(409, f"Workflow '{name}' is already running")

        root = Path(self.settings["server_root_dir"]).expanduser()
        yaml_path = root / ".nbpipe" / f"{name}.yaml"
        if not yaml_path.exists():
            yaml_path = root / ".nbpipe" / f"{name}.yml"
        if not yaml_path.exists():
            raise tornado.web.HTTPError(404, f"Workflow '{name}' not found")

        token = StopToken()
        _stop_tokens[name] = token
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _run_workflow, yaml_path, root, token)
        except WorkflowStoppedError:
            self.finish(json.dumps({"status": "stopped"}))
            return
        except Exception as exc:
            if token.is_stopped():
                self.finish(json.dumps({"status": "stopped"}))
                return
            raise tornado.web.HTTPError(500, str(exc))
        finally:
            _stop_tokens.pop(name, None)

        self.finish(json.dumps({"status": "ok"}))


class StopWorkflowHandler(APIHandler):
    @tornado.web.authenticated
    async def post(self, name):
        token = _stop_tokens.get(name)
        if token is None:
            raise tornado.web.HTTPError(404, f"No running workflow '{name}'")
        token.stop()
        self.finish(json.dumps({"status": "ok"}))


def _run_workflow(yaml_path: Path, base_dir: Path, stop_token: StopToken) -> None:
    workflow = load_workflow(yaml_path, base_dir=base_dir)
    for step in workflow.steps:
        if stop_token.is_stopped():
            raise WorkflowStoppedError("Workflow was stopped")
        execute_notebook(step.notebook, stop_token=stop_token)
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
            (
                url_path_join(base, "nbpipe", "workflows", r"([^/]+)", "stop"),
                StopWorkflowHandler,
            ),
        ],
    )
